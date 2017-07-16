import React from 'react';
import './NewsPanel.css';

import Auth from '../Auth/Auth';

import _ from 'lodash';

import NewsCard from '../NewsCard/NewsCard';

class NewsPanel extends React.Component {
    constructor() {
        super();
        // news is a list of news objs
        this.state = {
            news: null,
            pageNum:1,
            loadedAll:false
        };
        this.handleScroll = this.handleScroll.bind(this);
    }

    componentDidMount() {
        this.loadMoreNews();
        this.loadMoreNews = _.debounce(this.loadMoreNews, 1000);
        window.addEventListener('scroll', this.handleScroll);
    }

    handleScroll() {
        let scrollY = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
        if((window.innerHeight + scrollY) >= document.body.offsetHeight - 50) {
            console.log('Loading more for u...');
            this.loadMoreNews();
        }
    }

    loadMoreNews() {
        if (this.state.loadedAll === true) {
            console.log('all news have been loaded');
            return;
        }
        const url = 'http://localhost:3000/news/userId/' + Auth.getEmail()
                + '/pageNum/' + this.state.pageNum;
        const request = new Request(encodeURI(url), {
            method: 'GET',
            headers: {
                'Authorization': 'bearer ' + Auth.getToken(),
            },
            cache: false
        });
        
        fetch(request)
        .then((res) => {
            return res.json();
        })
        .then((news) => {
            if (!news || news.length === 0) {
                this.setState({loadedAll: true});
            }
            this.setState({
                news: this.state.news? this.state.news.concat(news) : news,
                pageNum: this.state.pageNum + 1
            });
        });
    }

    renderNews() {
        const newsList = this.state.news.map((aNews) => {
            return (
                <a className="list-group-item" href="#">
                    <NewsCard news={aNews} />
                </a>
            );
        });

        return (
            <div className="container-fluid">
                <div className="list-group">
                    {newsList}
                </div>
            </div>
        );
    }

    render() {
        if(this.state.news) {
            return (
                <div>
                    '{this.renderNews()}'
                </div>
            );
        }
        else {
            return(
                <div>
                    Loading...
                </div>
            );
        }
    }
}

export default NewsPanel;