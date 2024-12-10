const axios = require("axios");
const { v4: uuidv4 } = require("uuid");
const stun = require("stun");
const express = require("express");
const os = require("os");
const app = express();
let flagvalue = false;
app.use(express.json());

app.post("/server", (req, res) => {
  const { flag } = req.body;
  if (flag) {
    flagvalue = true;

    const code = uuidv4().slice(0, 8);

    const getPublicIP = async () => {
      try {
        const response = await stun.request("stun.l.google.com:19302");
        const { address } = response.getXorAddress(); // Public IP
        return address;
      } catch (error) {
        console.error("Error getting public IP:", error);
        return null;
      }
    };

    const getLocalIP = () => {
      const interfaces = os.networkInterfaces();
      for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
          if (iface.family === "IPv4" && !iface.internal) {
            return iface.address;
          }
        }
      }
      return null;
    };

    const localIP = getLocalIP();
    console.log("Local IP:", localIP);

    getPublicIP().then((publicIP) => {
      if (publicIP) {
        console.log("Public IP:", publicIP);
        sendIP(publicIP, localIP);
      } else {
        console.log("Failed to retrieve public IP.");
      }
    });

    const port = Math.floor(Math.random() * (65535 - 1024 + 1)) + 1024;

    const sendIP = async (publicIP, localIP) => {
      try {
        const response = await axios.post(
          "https://signaling-server-uj5n.onrender.com/ip",
          {
            publicIP: publicIP,
            localIP: localIP,
            code: code,
            port: port,
          }
        );
        const response1 = response.data;
        console.log("Response:", response.data);
        res.send(response1);
      } catch (error) {
        console.error("Error sending IP:", error);
        res.status(500).send("Error sending IP");
      }
    };
  }
});

app.listen(42069, () => {
  console.log("Server is running on port 42069");
});
