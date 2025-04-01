import { useEffect, useState } from "react";
import "./App.css";

interface Result {
  id: number;
  data: string;
  received_at: string;
}

const PAGE_SIZE = 15;

function App() {
  const [results, setResults] = useState<Result[]>([]);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    fetch("http://localhost/api/results")  // เปลี่ยนจาก localhost เป็น backend
      .then((response) => response.json())
      .then((data) => setResults(data))
      .catch((error) => console.error("Error fetching data:", error));
  }, []);
  

  const totalPages = Math.ceil(results.length / PAGE_SIZE);
  const paginatedResults = results.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);

  return (
    <div className="app-container">
      <h1>Database Results</h1>
      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Data</th>
              <th>Received At</th>
            </tr>
          </thead>
          <tbody>
            {paginatedResults.map((result) => (
              <tr key={result.id}>
                <td>{result.id}</td>
                <td>{result.data}</td>
                <td>{new Date(result.received_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="pagination">
        <button disabled={currentPage === 1} onClick={() => setCurrentPage((p) => p - 1)}>
          ◀ Prev
        </button>
        <span>Page {currentPage} of {totalPages}</span>
        <button disabled={currentPage === totalPages} onClick={() => setCurrentPage((p) => p + 1)}>
          Next ▶
        </button>
      </div>
    </div>
  );
}

export default App;