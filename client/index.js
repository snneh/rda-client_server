const axios = require("axios");
const readline = require("readline");
const stun = require("stun");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

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
  } else {
    console.log("Failed to retrieve public IP.");
  }
});

rl.question("Please enter the code: ", (cd) => {
  const getIp = async () => {
    try {
      const response = await axios.post("https://signaling-server-uj5n.onrender.com/getip", {
        code: cd,
      });
      console.log("response", response.data);
    } catch (error) {
      console.error("Error sending code:", error);
    }
  };

  getIp();
  rl.close();
});

