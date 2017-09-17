import Inferno from 'inferno';
import Component from 'inferno-component';

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
	'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export default class Shitpost extends Component {
	constructor(props) {
		super(props);
		
		this.hideShitpostModal = this.hideShitpostModal.bind(this);
	}
	
	getTime() {
		var time = this.props.time;
		return MONTHS[time.getMonth()] + " "
			+ time.getDay() + ", " + time.getFullYear()
			+ " at " + time.toLocaleTimeString();
	}
	
	hideShitpostModal(e) {
		this.props.modal('');
	}
	
	render() {
		return (
			<div className="outer-modal"
				onClick={this.hideShitpostModal}>
				<div className="shitpost-modal">
					<div className="Title">
						<p>{this.props.name} - Sentience</p>
						<div className="closeMe">X</div>
					</div>
					<div className="menus">
						<p>File</p>
						<p>Edit</p>
						<p>View</p>
						<p>Help</p>
						<p>Dream</p>
					</div>
					<img src={this.props.shitimg} />
					<div className="post">
						<h1>
							{this.props.shitpost}
						</h1>
						<p>
							{this.getTime()}
						</p>
					</div>
				</div>
			</div>
		);
	}
}