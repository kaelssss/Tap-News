var express = require('express');
var path = require('path');
var cors = require('cors');
var bodyParser = require('body-parser');
var passport = require('passport');

var index = require('./routes/index');
var news = require('./routes/news');
var auth = require('./routes/auth');
var config = require('./config/config.json');
var connectDb = require('./models/main');

var app = express();

// conn to mongoDb according to models/main and user
connectDb(config.mongoDbUri);
// following step used User Schema, must register first
// note: make sure in ur cs503-tn-db, add a USER
var authCheckerMiddleware = require('./middleware/authChecker');

// view engine setup
app.set('view engine', 'jade');
app.set('views', path.join(__dirname, '../tn-client/build'));

// this is how we server statics for React, cauz they build all the real static files
// in a separate dir: /static, while putting the index.html outside that
// so: OK, static files can be got at that latter dir u provided, but it will not fix the url path
// but remember: the default path url refers to the path of ur static html,
// if ur other statics are in deeper dir than index.html, u MUST mount a '/static' in this url
app.use('/static', express.static(path.join(__dirname, '../tn-client/build/static')));
// turn all stringified req bodies into real json objs
app.use(bodyParser.json());

// 3 things to do when using psp: init middware; define stg; use that stg as router
app.use(passport.initialize());
var localSignupStrategy = require('./passport/signup_passport');
var localLoginStrategy = require('./passport/login_passport');
passport.use('local-signup', localSignupStrategy);
passport.use('local-login', localLoginStrategy);

// TODO: remove this after development is done.
app.use(cors());

app.use('/', index);
app.use('/auth', auth);
app.use('/news', authCheckerMiddleware);
app.use('/news', news);

// catch 404
app.use(function(req, res) {
  var err = new Error('Not Found');
  err.status = 404;
  res.send('404 Not Found');
  //res.sendFile('index.html', { root: path.join(__dirname, '../tn-client/build') });
});

module.exports = app;