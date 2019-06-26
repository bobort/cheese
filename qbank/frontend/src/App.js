import './App.css';

import React, { Component } from 'react';
import { Button, Form } from 'react-bootstrap';

class App extends Component {
    constructor(props) {
        super(props);
        this.initialState = {
            answers: [],
            correct_answer: null,
            vignette: null,
            explanation: null
        };
        this.state = this.initialState;
    }
    renderAnswers = () => {
        const { answers, correct_answer } = this.state;
        return answers.map(item => (
            <li key={item.id} className="list-group-item d-flex justify-content-between">
                {item.id === correct_answer && <strong>Correct.</strong>}
                <span className="answer">{ item.description }</span>
                <Button variant="secondary" className="mr-2"> Edit </Button>
                <Button variant="danger">Delete </Button>
            </li>
        ));
    }
    render() {
        const { vignette, explanation } = this.state;
        return (
            <div className="content">
                <h1 className="text-white text-uppercase text-center my-4">Question Bank Creation App</h1>
                <div className="row">
                    <Button variant="primary">Add question</Button>
                    <Form className="col-lg-8 col-md-6">
                        <Form.Label>
                            Enter the vignette:
                        </Form.Label>
                        <Form.Control as="textarea" rows="7" value={vignette}>
                        </Form.Control>
                        <ul className="list-group list-group-flush">
                            {this.renderAnswers()}
                        </ul>
                    </Form>
                </div>
            </div>
        );
    }
}
export default App;
