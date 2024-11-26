const axios = require("axios");
const { v4: uuidv4 } = require("uuid");
const stun = require("stun");


const code = uuidv4().slice(0, 8);
const getPublicIP = async () => {
  try {
    const response = await stun.request("stun.l.google.com:19302");
    const { address } = response.getXorAddress();//apparantly this is the public ip
    return address;
  } catch (error) {
    console.error("Error getting public IP:", error);
    return null;
  }
};

getPublicIP().then((publicIP) => {
  if (publicIP) {
    console.log("Public IP:", publicIP);
    sendIP(publicIP);
  } else {
    console.log("Failed to retrieve public IP.");
  }
});

const port = Math.floor(Math.random() * (65535 - 1024 + 1)) + 1024;
const sendIP = async (publicIP) => {
  try {
    const response = await axios.post("http://localhost:3000/ip", {
      ip: publicIP,
      code: code,
      port: port,
    });
    console.log("response", response.data);
  } catch (error) {
    console.error("Error sending IP:", error);
  }
};