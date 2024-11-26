const os = require("os");

const interfaces = os.networkInterfaces();
const addresses = [];
for (const name of Object.keys(interfaces)) {
  for (const iface of interfaces[name]) {
    if ("IPv4" !== iface.family || iface.internal !== false) {
      continue;
    }

    addresses.push(iface.address);
  }
}

const myIP = addresses[0];
console.log(myIP);
