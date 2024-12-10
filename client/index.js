const axios = require("axios");
const stun = require("stun");
const express = require("express");
const os = require("os");

const app = express();
const port = 6969;

// Middleware to parse JSON bodies
app.use(express.json());

app.post("/client", async (req, res) => {
  const { code } = req.body; // Destructure the code from the request body

  try {
    // Fetch public IP using STUN
    const getPublicIP = async () => {d378f9ef
      try {
        const response = await stun.request("stun.l.google.com:19302");
        const { address } = response.getXorAddress();
        return address;
      } catch (error) {
        console.error("Error getting public IP:", error);
        return null;
      }
    };

    // Fetch local IP using os module
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

    const publicIP = await getPublicIP();
    const localIP = getLocalIP();

    if (publicIP) {
      console.log("Public IP:", publicIP);
    } else {
      console.log("Failed to retrieve public IP.");
    }

    console.log("Local IP:", localIP);

    // Send code to signaling server and get the response
    const response = await axios.post(
      "https://signaling-server-uj5n.onrender.com/getip",
      {
        code: code,
        publicIP: publicIP,
        localIP: localIP,
      }
    );

    console.log("Response from signaling server:", response.data);

    // Send the signaling server's response back to the client
    res.json(response.data);
  } catch (error) {
    console.error("Error in /client route:", error.message);
    res.status(500).json({ error: "An error occurred" });
  }
});

app.listen(port, () => {
  console.log(`Example app listening at http://localhost:${port}`);
});
