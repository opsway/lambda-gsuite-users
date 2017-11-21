const mysql    = require('mysql');
module.exports = function(app, db) {
    app.post('/webhooks', (req, res) => {

        let connection = mysql.createConnection({
          host     : process.env.DB_HOST || 'localhost',
          port     : process.env.DB_PORT || '3306',
          database : process.env.DB_NAME || 'database',
          user     : process.env.DB_USER || 'user',
          password : process.env.DB_PASS || 'password'
        });

        let result = {};
        switch (req.body.action) {
            case 'change_commission':
                let event = req.body.event || {};
                connection.connect();
                connection.query('UPDATE settings SET value = ? WHERE name = ?', [event.value,  event.fund], function (error, results, fields) {
                  result = results;
                  if (error) {
                      result = results;
                  }
                  res.json(result);
                });

                connection.end();
                break;
            default:
                res.json(result);
        }

      });
};
