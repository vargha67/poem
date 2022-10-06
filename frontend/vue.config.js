const configureAPI = require("./src/server/config.js");

module.exports = {
  devServer: {
    onBeforeSetupMiddleware: (devServer) => {
    	configureAPI(devServer.app)
    }
  }
};
