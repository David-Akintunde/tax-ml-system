import React, { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { downloadCSV } from '../utils/exportCSV';
import AnimatedPage from './AnimatedPage';

const RevenueForecast = () => {
  const [months, setMonths] = useState(new Array(12).fill(1000000));
  const [forecast, setForecast] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (index: number, value: string) => {
    const newMonths = [...months];
    newMonths[index] = parseFloat(value);
    setMonths(newMonths);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/predict/forecast', {
        last_12_months: months,
      });
      setForecast(response.data.forecast);
      toast.success('Forecast generated.');
    } catch (error) {
      console.error(error);
      toast.error('Error calling API. Ensure backend is running on port 5000.');
    }
    setLoading(false);
  };

  const handleExport = () => {
    if (forecast === null) {
      toast.error('Please generate a forecast first.');
      return;
    }
    const exportData = months.map((val, idx) => ({
      month_index: idx + 1,
      historical_revenue: val,
      note: '',
    }));
    exportData.push({
      month_index: 13,
      historical_revenue: forecast,
      note: 'Forecasted value',
    });
    downloadCSV(exportData, `revenue_forecast_${new Date().toISOString().slice(0, 19)}`);
    toast.success('Exported to CSV');
  };

  return (
    <AnimatedPage>
      <div className="bg-white p-6 rounded shadow">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">Revenue Forecast (LSTM)</h2>
          {forecast !== null && (
            <button
              onClick={handleExport}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-transform duration-200 hover:scale-105"
            >
              Export to CSV
            </button>
          )}
        </div>
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-3 gap-4">
            {months.map((val, idx) => (
              <div key={idx}>
                <label className="block text-sm font-medium">Month {idx + 1}</label>
                <input
                  type="number"
                  value={val}
                  onChange={(e) => handleChange(idx, e.target.value)}
                  className="mt-1 block w-full border rounded p-2"
                />
              </div>
            ))}
          </div>
          <button
            type="submit"
            className="mt-4 bg-green-600 text-white px-4 py-2 rounded transition-transform duration-200 hover:scale-105"
            disabled={loading}
          >
            {loading ? 'Loading...' : 'Forecast Next Month'}
          </button>
        </form>
        {forecast !== null && (
          <div className="mt-6 p-4 bg-gray-100 rounded">
            <h3 className="font-bold">Predicted Revenue for Next Month:</h3>
            <p className="text-2xl">₦{forecast.toLocaleString()}</p>
          </div>
        )}
      </div>
    </AnimatedPage>
  );
};

export default RevenueForecast;