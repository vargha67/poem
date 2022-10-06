const express = require("express");
const api = require("./api.js");

module.exports = (app) => {
  app.use(express.json());
  //app.use(express.static("../../data"))
  app.use("/api", api);
};
