import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import './resume_analyzer.css'; // Import the CSS file

const ResumeAnalyzer = () => {

  // State to manage input values and recommendations
  const [jobDescription, setJobDescription] = useState('');
  const [similarityReport, setSimilarityReport] = useState('');
  const [files, setFiles] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('job_description', jobDescription);

    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const response = await axios.post('https://127.0.0.1:5000/calculate_similarity', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSimilarityReport(response.data.similarity_report);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleReset = () => {
    setJobDescription(''); // Reset form data to its initial state
    setSimilarityReport('');
  };

  const exportToExcel = () => {
    const ws = XLSX.utils.json_to_sheet(similarityReport);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Similarity Report");

    // Generate the Excel file as an ArrayBuffer
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });

    // Convert the ArrayBuffer to a Blob
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });

    // Prompt the user to select a folder to save the file
    saveAs(blob, 'similarity_report.xlsx');
  };
  
    return (
        <div className='grid-container'>
          <div className="result-box-container">
            <div>
              <h1 className='blue-hedding'>Resume Analyzer</h1>
            </div>
            <div className='input-container-item'>
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="Textarea">Job Description</label>
                  <textarea 
                    className="form-control" 
                    id="exampleFormControlTextarea1" 
                    rows="10"
                    placeholder="Enter Job Description"
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    required
                  >
                  </textarea>
                </div>
                <div className="form-group">
                  <label htmlFor="folder_path" className="col-sm-6 col-form-label">Folder Path</label>
                  <div className="col-sm-12">
                    <input
                      type="file"
                      className="form-control"
                      id="resumeFiles"
                      name="resumeFiles"
                      placeholder="Select the resume files"
                      multiple
                      onChange={(e) => setFiles(e.target.files)}
                      required 
                    />
                  </div>
                </div>
                <button type="submit" className="btn btn-primary add-btn">
                  Analyze
                </button>
                <button type="button" className="btn btn-outline-primary clear-btn" onClick={handleReset}>
                  Reset
                </button>
              </form>              
            </div>
          </div>
                <div className="result-box-container">
                  <div>
                    <h1 className='blue-hedding'>Similarity Report</h1>
                  </div>
                  <div className='input-container-item'>
                    {similarityReport && 
                      <div>
                        <div className='container-item'>
                          <div className="scroll-item">
                            <table className="table table-hover">
                              <thead>
                                <tr>
                                  <th scope="col">Resume</th>
                                  <th scope="col">Similarity</th>
                                </tr>
                              </thead>
                              <tbody>
                                {similarityReport.map((item, index) => (
                                  <tr key={index}>
                                    <td className="table-text">{item.Resume}</td>
                                    <td>{item.Similarity}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                        <div>
                          <button className="btn btn-primary add-btn" onClick={exportToExcel}>Export to Excel</button>
                        </div>
                      </div>
                    }
                  </div>
                </div>
        </div>
    );
  };

export default ResumeAnalyzer;
