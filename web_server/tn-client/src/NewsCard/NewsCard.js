import React from 'react';
import Auth from '../Auth/Auth';
import './NewsCard.css';

class NewsCard extends React.Component {
    constructor() {
        super();
        this.state = {
            rate: 0
        }
        
        this.redirectToUrl = this.redirectToUrl.bind(this);
        this.likeNews = this.likeNews.bind(this);
        this.dislikeNews = this.dislikeNews.bind(this);
    }

    redirectToUrl(event) {
        event.preventDefault();
        //this.sendClickLog(1);
        window.open(this.props.news.url, '_blank');
    }

    likeNews(event) {
        event.preventDefault();
        this.sendClickLog(1);
        this.setState({
            rate: this.state.rate + 1
        });
    }

    dislikeNews(event) {
        event.preventDefault();
        this.sendClickLog(-1);
        this.setState({
            rate: this.state.rate - 1
        });
    }

    sendClickLog(rate) {
        let url_part1 = Auth.getEmail();
        let url_part2 = this.props.news.digest;
        //let encodedUrl = encodedURI(url_part1 + url_part2)
        let encodedUrl2 = 'http://localhost:3000/news/userId/' + encodeURIComponent(url_part1) + '/newsId/' + encodeURIComponent(url_part2)
        let request = new Request(encodedUrl2, {
            method: 'POST',
            headers: {
                'Authorization': 'bearer ' + Auth.getToken(),
                'rate': rate
            },
            cache: false
        });
        fetch(request);
    }

    render() {
        let btnLeft = null
        let btnRight = null
        if(this.state.rate === 1) {
            btnLeft = (<a className="waves-effect waves-light btn" onClick={this.dislikeNews}>undo</a>)
            btnRight = (<a className="btn-flat disabled">liked</a>)
        }
        else if(this.state.rate === -1) {
            btnLeft = (<a className="btn-flat disabled">disliked</a>)
            btnRight = (<a className="waves-effect waves-light btn" onClick={this.likeNews}>undo</a>)
        }
        else {
            btnLeft = (<a className="waves-effect waves-light btn" onClick={this.likeNews}>like</a>)
            btnRight = (<a className="waves-effect waves-light btn" onClick={this.dislikeNews}>dislike</a>)
        }

        return (
            <div className="news-container disabled">
                <div className='row'>
                <div className='col s4 fill'>
                    <img src={this.props.news.urlToImage} alt='news'/>
                </div>
                <div className="col s8">
                    <div className="news-intro-col">
                        <div className="news-intro-panel">
                            <h4>{this.props.news.title}</h4>
                            <div className="news-description">
                                <p>{this.props.news.description}</p>
                                <div>
                                    {this.props.news.source != null && <div className='chip light-blue news-chip'>{this.props.news.source}</div>}
                                    {this.props.news.class != null && <div className='chip light-green news-chip'>{this.props.news.class}</div>}
                                    {this.props.news.time != null && <div className='chip amber news-chip'>{this.props.news.time}</div>}
                                </div>
                                <a className="waves-effect waves-light btn" onClick={this.redirectToUrl}>goto</a>
                                {btnLeft}
                                {btnRight}
                            </div>
                        </div>
                    </div>
                </div>
                </div>
            </div>
        );
    }
}

export default NewsCard;