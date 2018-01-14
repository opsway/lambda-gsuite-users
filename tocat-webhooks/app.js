const express        = require('express');
const basicAuth = require('express-basicauth');
const bodyParser     = require('body-parser');
const app            = express();
const port = process.env.APP_PORT || 8000;
const username = process.env.APP_USER || 'test';
const password = process.env.APP_PASS || 'test';
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(basicAuth({username: username, password: password}));
require('./routes')(app, {});

app.listen(port, () => {
  console.log('We are live on ' + port);
});

module.exports = app;
