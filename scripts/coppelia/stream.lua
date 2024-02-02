sim=require'sim'

custom={
    menu='Connectivity\nCustom Visualization stream',
    rootResource='threejsFrontend.html',
    paramNamespace='customvisualizationStream',
}
pcall(function()
    for k,v in pairs(require'threejsFrontend-custom') do
        custom[k]=v
    end
end)

function P(n)
    -- parameters namespace
    return custom.paramNamespace..'.'..n
end

function sysCall_info()
	return {autoStart = true,menu=custom.menu}
    --return {autoStart=sim.getNamedBoolParam(P'autoStart')==true,menu=custom.menu}
end

function sysCall_init()
    cbor=require'org.conman.cbor'
    base64=require'base64'
    url=require'socket.url'

    sentGenesis={}
    resourcesDir=sim.getStringParameter(sim.stringparam_resourcesdir)

    zmqEnable=sim.getNamedBoolParam(P'zmq.enable')
    wsEnable=sim.getNamedBoolParam(P'ws.enable')
    if wsEnable==nil then wsEnable=true end

    if zmqEnable then
        simZMQ=require'simZMQ'
        simZMQ.__raiseErrors(true) -- so we don't need to check retval with every call
        zmqPUBPort=sim.getNamedInt32Param(P'zmq.pub.port') or 23010
        zmqREPPort=sim.getNamedInt32Param(P'zmq.rep.port') or (zmqPUBPort+1)
        print('ZMQ endpoint on ports '..tostring(zmqPUBPort)..', '..tostring(zmqREPPort)..'...')
        zmqContext=simZMQ.ctx_new()
        zmqPUBSocket=simZMQ.socket(zmqContext,simZMQ.PUB)
        simZMQ.bind(zmqPUBSocket,string.format('tcp://*:%d',zmqPUBPort))
        zmqREPSocket=simZMQ.socket(zmqContext,simZMQ.REP)
        simZMQ.bind(zmqPUBSocket,string.format('tcp://*:%d',zmqREPPort))
    end

    if wsEnable then
        simWS=require'simWS'
        wsPort=sim.getNamedInt32Param(P'ws.port') or 23020
        print('WS endpoint on port '..tostring(wsPort)..'...')
        if sim.getNamedBoolParam(P'ws.retryOnStartFailure') then
            while true do
                local r,e=pcall(function() wsServer=simWS.start(wsPort) end)
                if r then break end
                print('WS failed to start ('..e..'). Retrying...')
                sim.wait(0.5,false)
            end
        else
            wsServer=simWS.start(wsPort)
        end
        simWS.setOpenHandler(wsServer,'onWSOpen')
        simWS.setCloseHandler(wsServer,'onWSClose')
        simWS.setMessageHandler(wsServer,'onWSMessage')
        simWS.setHTTPHandler(wsServer,'onWSHTTP')
        wsClients={}
    end

    if not zmqEnable and not wsEnable then
        sim.addLog(sim.verbosity_errors,'aborting because no RPC backend selected')
        return {cmd='cleanup'}
    end
end

function sysCall_addOnScriptSuspend()
    return {cmd='cleanup'}
end

function sysCall_nonSimulation()
    processZMQRequests()
end

function sysCall_sensing()
    processZMQRequests()
end

function sysCall_suspended()
    processZMQRequests()
end

function sysCall_event(data)
    sendEventRaw(data)
end

function sysCall_cleanup()
    if zmqPUBSocket or zmqREPSocket then
        if zmqPUBSocket then simZMQ.close(zmqPUBSocket) end
        if zmqREPSocket then simZMQ.close(zmqREPSocket) end
        simZMQ.ctx_term(zmqContext)
    end

    if wsServer then
        simWS.stop(wsServer)
    end
end

function getFileContents(path)
    local f,err,errno=io.open(path,"rb")
    if f then
        local content=f:read("*all")
        f:close()
        return 200,content
    else
        return 404,nil
    end
end

function processZMQRequests()
    if not zmqREPSocket then return end
    while true do
        local rc,revents=simZMQ.poll({zmqREPSocket},{simZMQ.POLLIN},0)
        if rc<=0 then break end
        local rc,req=simZMQ.recv(zmqREPSocket,0)
        req=cbor.decode(req)
        local resp=''
        if req.cmd=='getbacklog' then
            resp=sim.getGenesisEvents()
        else
            sim.addLog(sim.verbosity_errors,'unrecognized request')
            print(req)
        end
        simZMQ.send(zmqREPSocket,resp,0)
    end
end

function onWSOpen(server,connection)
    if server==wsServer then
        wsClients[connection]=1
        sendEventRaw(sim.getGenesisEvents(),connection)
        sentGenesis[connection]=1
    end
end

function onWSClose(server,connection)
    if server==wsServer then
        wsClients[connection]=nil
    end
end

function onWSMessage(server,connection,message)
end

function onWSHTTP(server,connection,resource,requestdata)
    resource=url.unescape(resource)
    local status,data=404,nil

		
	if resource == '/loadscene' then
        if requestdata then
            -- Using pcall for error handling
            local success, err = pcall(sim.loadScene, requestdata)
            if success then
                return 200, "Scene loaded: " .. requestdata
            else
                -- Handle the error
                sim.addLog(sim.verbosity_errors, 'Error loading scene: ' .. err)
                return 500, "Error loading scene"
            end
        else
            return 400, "No data received"
        end
    end

		
	
	
	if resource=='/start' then sim.startSimulation() return 200, "Simulation Started" end
	if resource=='/stop' then sim.stopSimulation() return 200, "Simulation Stoped" end
	
    if resource=='/' then resource='/'..custom.rootResource end
    if any(function(ext) return string.endswith(resource,'.'..ext) end,{'html','htm','css','js','js.map'}) then
        status,data=getFileContents(resourcesDir..resource)
        if status==200 and string.endswith(resource,'.html') then
            data=string.gsub(data,'const wsPort = 23020;','const wsPort = '..wsPort..';')
            data=string.gsub(data,string.escpat'<!--[[CUSTOM_HTML]]-->',custom.extraHTML or '')
            data=string.gsub(data,string.escpat'<!--[[CUSTOM_HELP]]-->',custom.extraHelp or '')
        end
    end
    if status==404 and resource~='/favicon.ico' then
        sim.addLog(sim.verbosity_errors,'resource not found: '..resource)
    end
    return status,data
end

function sendEventRaw(d,conn)
    if d==nil then return end

    if zmqPUBSocket then
        simZMQ.send(zmqPUBSocket,d,0)
    end
    if wsServer then
        for connection,_ in pairs(wsClients) do
            -- broadcast only after genesis
            if (conn==nil and sentGenesis[connection]) or conn==connection then
                simWS.send(wsServer,connection,d,simWS.opcode.binary)
            end
        end
    end
end

function verbose()
    return sim.getNamedInt32Param(P'verbose') or 0
end
