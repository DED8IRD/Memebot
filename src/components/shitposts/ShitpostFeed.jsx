import Inferno from 'inferno';
import Component from 'inferno-component';
import Shitpost from './Shitpost';

export default class ShitpostFeed extends Component {
	constructor(props) {
		super(props);
	}
	
	displayShitposts() {
		var length = this.props.shitposts.length;
		var shitposts = [];
		for (var i = 0; i < length; ++i) {
			var shit = this.props.shitposts[i];
			var shitpost = (
				<Shitpost key={i}
					id={shit.id}
					name={shit.name}
					votes={shit.votes}
					time={shit.time}
					shitpost={shit.post}
					shitimg={shit.img}
					modal={this.props.modal} />
			);
			shitposts.push(shitpost);
		}
		return shitposts;
	}
	
	render() {
		return (
			<div className="shitpost-feed">
				{this.displayShitposts()}
			</div>
		);
	}
}