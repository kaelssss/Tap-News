import React from 'react';
import PropTypes from 'prop-types';
import LoginForm from './LoginForm';
import Auth from '../Auth/Auth';

class LoginPage extends React.Component {
    constructor(props, context) {
        super(props, context);
        this.state = {
            errors: {
                summary: '',
                email: '',
                password: ''
            },
            userInfo: {
                email: '',
                password: ''
            }
        };
        this.processForm = this.processForm.bind(this);
        this.changeInfo = this.changeInfo.bind(this);
    }

    processForm(event) {
        event.preventDefault();
        const email = this.state.userInfo.email;
        const password = this.state.userInfo.password;
        fetch('http://localhost:3000/auth/login', {
            method: 'POST',
            cache: false,
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: this.state.userInfo.email,
                password: this.state.userInfo.password
            })
        }).then(res => {
            if(res.status === 200) {
                this.setState({
                    errors: {}
                });
                res.json().then((json) => {
                    console.log(json);
                    Auth.authenticateUser(json.token, email);
                    this.context.router.replace('/');
                });
            }
            else {
                console.log('login failed');
                res.json().then((json) => {
                    const errors = json.errors? json.errors:{};
                    errors.summary = json.message;
                    this.setState({
                        errors: errors
                    });
                });
            }
        });
    }

    changeInfo(event) {
        const field = event.target.name;
        const userInfo = this.state.userInfo;
        userInfo[field] = event.target.value;
        this.setState({
            userInfo: userInfo
        });
    }

    render() {
        return (
            <LoginForm 
                onSubmit={this.processForm}
                onChange={this.changeInfo}
                errors={this.state.errors}
            />
        );
    };
}

LoginPage.contextTypes = {
    router: PropTypes.object.isRequired
};

export default LoginPage;