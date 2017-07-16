var mongoose = require('mongoose');

// this could have been done in app.js like pj1, but we just define them here and call it in app.js
var connect = function(uri) {
    mongoose.connect(uri);
    mongoose.connection.on('error', (err) => {
        console.error('Mongoose connection err: %{err}');
        process.exit(1);
    });
    // load that User Schema here
    require('./user');
}

module.exports = connect;