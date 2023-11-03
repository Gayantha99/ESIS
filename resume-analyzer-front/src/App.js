import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ResumeAnalyzer from './components/Resume_analyzer';



function App() {
  return (
    <Router>
      <Routes>
        <Route exact path="/" element={<ResumeAnalyzer />} />
      </Routes>
    </Router>
  );
}

export default App;
