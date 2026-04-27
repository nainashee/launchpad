import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Nav from './components/Nav';
import Dashboard from './pages/Dashboard';
import TailorResume from './pages/TailorResume';
import JobDecoder from './pages/JobDecoder';
import Applications from './pages/Applications';

export default function App() {
  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/tailor" element={<TailorResume />} />
        <Route path="/decode" element={<JobDecoder />} />
        <Route path="/applications" element={<Applications />} />
      </Routes>
    </BrowserRouter>
  );
}
