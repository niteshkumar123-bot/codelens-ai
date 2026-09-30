'use client';

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { getProjects, createProject, analyzeCode } from '@/lib/api';
import { AnalysisReport, Project } from '@/types';

const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });

const starterCode = `def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []`;

export default function CodeAnalyzerPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState('');
  const [code, setCode] = useState(starterCode);
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getProjects()
      .then((data) => {
        setProjects(data);
        if (data.length > 0) setSelectedProject(data[0].id);
      })
      .catch(() => setError('Could not connect to the backend. Make sure Docker Compose is running.'));
  }, []);

  async function handleAnalyze() {
    setLoading(true);
    setError('');
    try {
      let projectId = selectedProject;
      if (!projectId) {
        const project = await createProject('Default Project', 'Auto-created project');
        projectId = project.id;
        setSelectedProject(projectId);
        setProjects((current) => [...current, project]);
      }
      const result = await analyzeCode(projectId, code);
      setReport(result);
    } catch (err) {
      console.error(err);
      setError('Analysis failed. Check the backend logs for details.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>CodeLens AI</h1>
      <p>Python code evaluation, debugging and static analysis.</p>

      <section className="card">
        <div className="row">
          <label htmlFor="project">Project:</label>
          <select id="project" className="select" value={selectedProject} onChange={(e) => setSelectedProject(e.target.value)}>
            <option value="">Create default project</option>
            {projects.map((project) => <option key={project.id} value={project.id}>{project.name}</option>)}
          </select>
          <button className="button" onClick={handleAnalyze} disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze Code'}
          </button>
        </div>
      </section>

      {error && <section className="card"><strong>Error:</strong> {error}</section>}

      <section className="card">
        <h2>Python Code</h2>
        <MonacoEditor
          height="430px"
          defaultLanguage="python"
          value={code}
          onChange={(value) => setCode(value ?? '')}
          options={{ minimap: { enabled: false }, fontSize: 14 }}
        />
      </section>

      <section className="card">
        <h2>Analysis Report</h2>
        {!report ? (
          <p>Click &quot;Analyze Code&quot; to run the analysis.</p>
        ) : (
          <>
            <div className="row">
              <div><div>Overall Score</div><div className="metric">{report.overall_score}/100</div></div>
              <div><div>Syntax</div><div>{report.syntax_valid ? '✅ Valid' : '❌ Invalid'}</div></div>
            </div>
            <h3>Findings ({report.findings.length})</h3>
            {report.findings.length === 0 ? <p>No findings.</p> : report.findings.map((finding, index) => (
              <div className="finding" key={`${finding.rule_id}-${index}`}>
                <strong>{finding.severity}: {finding.title}</strong>
                <p>{finding.description}</p>
                {finding.recommendation && <small>Recommendation: {finding.recommendation}</small>}
              </div>
            ))}
            {report.test_runs?.[0] && (
              <div>
                <h3>Automated Test Execution</h3>
                <p>Passed: {report.test_runs[0].passed_tests} / Failed: {report.test_runs[0].failed_tests}</p>
                <pre>{report.test_runs[0].execution_output}</pre>
              </div>
            )}
          </>
        )}
      </section>
    </main>
  );
}
