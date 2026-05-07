"use client";
import React, { useEffect, useState } from "react";

export default function Page2() {
  const [data, setData] = useState<{ dataset: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/stats?sources=true")
      .then((res) => res.json())
      .then((json) => {
        const sources = json.sources || [];
        // ✅ Dataset 이름 기준으로 알파벳순 정렬
        const sorted = sources.sort((a, b) =>
          a.dataset.localeCompare(b.dataset)
        );
        setData(sorted);
      })
      .catch((err) => console.error("❌ Fetch error:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-center py-10">Loading...</p>;

  return (
    <main className="p-8 bg-white min-h-screen">
      <h1 className="text-2xl font-bold mb-6 text-gray-800">🗂 Data Sources (A–Z)</h1>
      <table className="w-full border-collapse border border-gray-200 text-sm">
        <thead className="bg-gray-50 text-gray-700">
          <tr>
            <th className="border p-2 text-left">Dataset</th>
            <th className="border p-2 text-right">Count</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className="hover:bg-blue-50 transition">
              <td className="border p-2 font-semibold text-blue-700">{row.dataset}</td>
              <td className="border p-2 text-right">{row.count.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
