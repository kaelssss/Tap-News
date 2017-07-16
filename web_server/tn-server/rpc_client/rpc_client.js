var jayson = require('jayson');

var client = jayson.client.http({
    port: 4040,
    hostname: 'localhost'
});

function add(a, b, callback) {
    client.request('add', [a, b], function(err, error, response) {
        if (err) throw err;
        console.log(response);
        callback(response);
    });
}

function getNewsSummariesForUser(user_id, page_num, callback) {
    client.request('getNewsSummariesForUser', [user_id, page_num], function(err, error, res) {
        if (err) throw err;
        console.log(res);
        callback(res);
    });
}

function logNewsClickForUser(user_id, news_id, rate) {
    client.request('logNewsClickForUser', [user_id, news_id, rate], function(err, error, response) {
        if (err) throw err;
        console.log(response);
    });
}

module.exports = {
    add: add,
    getNewsSummariesForUser: getNewsSummariesForUser,
    logNewsClickForUser: logNewsClickForUser
};