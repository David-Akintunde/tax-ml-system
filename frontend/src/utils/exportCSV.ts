// utils/exportCSV.ts
export const downloadCSV = (data: any[], filename: string) => {
  if (!data.length) return;

  // Get headers from first object
  const headers = Object.keys(data[0]);
  // Convert each row to array of values
  const rows = data.map(row => headers.map(header => JSON.stringify(row[header] ?? '')));
  // Combine headers + rows
  const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
  // Create blob and download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  link.href = url;
  link.setAttribute('download', `${filename}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};