CryptoJS = require("crypto-js");

const args = process.argv.slice(2);

console.log(CryptoJS.AES.encrypt(args[0], args[1]).toString());
