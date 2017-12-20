<template>
<div id="app">
    <div v-if="pickerOpen" id="colorPicker">
        R:<input type="text" name="R" v-model="pickerColor.R">
        G:<input type="text" name="G" v-model="pickerColor.G">
        B:<input type="text" name="B" v-model="pickerColor.B">
        <div id="colorbox" style="background-color:rgb(pickerColor.R, pickerColor.G, pickerColor.B)"></div>
        <button id="pickerOK" v-on:click="pickerOpen=false;pickerValue=pickerColor">OK</button>
        <button id="pickerCancel" v-on:click="pickerOpen=false">Cancel</button>
    </div>
    <ul>
        <li v-for="(value, key) in attributes">
            <div>{{key}}</div>
            <input v-if="attributesType[key] == 'float'" type="text" name="key" v-model="attributes[key]">
            <input v-if="attributesType[key] == 'int'" type="text" name="key" v-model="attributes[key]">

            <div v-on:click="pickerOpen=true;pickerValue=attributes[key]" v-if="attributesType[key] == 'color'" id="colorBox" style="background-color:rgb(value[0], value[1], value[2])"></div>

            <input v-if="attributesType[key] == 'bool'" type="checkbox" name="key" v-model="attributes[key]">

        </li>
    </ul>
    <button id="updateButton" v-on:click="updateAttributes">Update</button>
</div>
</template>

<script>
export default {
    name: 'app',
    data () {
        return {
            msg: 'Welcome to LED Manipulator',
            websocket: null,
            attributes: {
                "rainbow" : "",
                "rainbowStartValue" : "",
                "rainbowInversion" : "",
                "frequencySaturation" : "",
                "individualLEDAmplitudes" : "",
                "defaultBaseColor" : [],
                "bassColor" : [],
                "midColor" : [],
                "highColor" : [],
                "useBassDeppression" : "",
                "useMidDeppression" : "",
                "useHighDeppression" : "",
            },
            attributesType: {
                "rainbow" : "bool",
                "rainbowStartValue" : "float",
                "rainbowInversion" : "bool",
                "frequencySaturation" : "bool",
                "individualLEDAmplitudes" : "bool",
                "defaultBaseColor" : "color",
                "bassColor" : "color",
                "midColor" : "color",
                "highColor" : "color",
                "useBassDeppression" : "bool",
                "useMidDeppression" : "bool",
                "useHighDeppression" : "bool",
            },
            client : null,
            connection : null,
            pickerColor : {
                R : "0",
                G : "0",
                B : "0"
            },
            pickerOpen : false,
            pickerValue : null
        }
    },
    created: () => {

        var that = this;

        var WebSocketClient = require('websocket').client;

        that.$data.client = new WebSocketClient();

        client.on('connectFailed', function(error) {
            console.log('Connect Error: ' + error.toString());
        });

        client.on('connect', function(connection) {
            console.log('WebSocket Client Connected');
            connection.on('error', function(error) {
                console.log("Connection Error: " + error.toString());
            });
            connection.on('close', function() {
                console.log('echo-protocol Connection Closed');
            });
            connection.on('message', function(message) {
                if (message.type === 'utf8') {
                    if(len(message.utf8Data) > 50)
                        attributes = JSON.parse(message.utf8Data)
                    else
                        console.log(message.utf8Data)
                }
            });

            connection.sendUTF("webclient");
            that.$data.connection = connection
        });

        client.connect('ws://192.168.0.26:12345/', 'echo-protocol');

    },
    methods : {
        updateAttributes : function() {
            var that = this;
            that.$data.connection.sendUTF(JSON.stringify(that.$data.attributes))
        }
    }
}
</script>

<style lang="scss">
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

h1, h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  display: inline-block;
  margin: 0 10px;
}

a {
  color: #42b983;
}
</style>
