import { Routes, Route } from 'react-router-dom'
import Layout from './layouts/Layout'
import Dashboard from './pages/Dashboard'
import FundDetails from './pages/FundDetails'
import Compare from './pages/Compare'
import Rankings from './pages/Rankings'
import Metadata from './pages/Metadata'
import Glossary from './pages/Glossary'
import Quality from './pages/Quality'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="fund/:ticker" element={<FundDetails />} />
        <Route path="compare" element={<Compare />} />
        <Route path="rankings" element={<Rankings />} />
        <Route path="metadata" element={<Metadata />} />
        <Route path="glossary" element={<Glossary />} />
        <Route path="quality" element={<Quality />} />
      </Route>
    </Routes>
  )
}

export default App
