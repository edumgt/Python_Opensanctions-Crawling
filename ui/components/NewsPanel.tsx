"use client";
import React, { useEffect, useState } from "react";

interface WPPost {
  id: number;
  title: { rendered: string };
  excerpt: { rendered: string };
  link: string;
  date: string;
  yoast_head?: string;
}

export default function NewsPanel() {
  const [posts, setPosts] = useState<WPPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchNews() {
      try {
        const res = await fetch("https://www.sanctionlab.com/?rest_route=/wp/v2/posts");
        const data = await res.json();
        setPosts(data);
      } catch (err) {
        console.error("❌ Failed to fetch news:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchNews();
  }, []);

  if (loading) return <p className="text-gray-500 text-sm">Loading latest news...</p>;

  return (
    <div className="overflow-y-auto max-h-[80vh]">
      {posts.length === 0 ? (
        <p className="text-gray-400 text-sm">No news available.</p>
      ) : (
        <ul className="space-y-5">
          {posts.map((post) => (
            <li key={post.id} className="border-b pb-3">
              {/* 제목 */}
              <a
                href={post.link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-700 font-bold hover:underline"
                dangerouslySetInnerHTML={{ __html: post.title.rendered }}
              />
              {/* 날짜 */}
              <div className="text-xs text-gray-400 mt-1">
                {new Date(post.date).toLocaleDateString("ko-KR", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </div>
              {/* 요약 */}
              <div
                className="text-gray-700 text-sm mt-2"
                dangerouslySetInnerHTML={{
                  __html: post.excerpt.rendered.replace(/\[&hellip;\]/g, "..."),
                }}
              />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
