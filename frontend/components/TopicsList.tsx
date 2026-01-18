'use client'

interface TopicsListProps {
  sessionId: string
  topics: string[]
  onStartQuiz: (type: 'initial' | 'adaptive') => void
  onViewStats: () => void
}

export default function TopicsList({ sessionId, topics, onStartQuiz, onViewStats }: TopicsListProps) {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-800">
          Extracted Topics
        </h2>
        <button
          onClick={onViewStats}
          className="text-primary-600 hover:text-primary-700 font-medium"
        >
          View Stats
        </button>
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-sm text-gray-600 mb-4">
          Found {topics.length} topics in your syllabus:
        </p>
        <ul className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {topics.map((topic, index) => (
            <li
              key={index}
              className="bg-white px-4 py-2 rounded-lg shadow-sm border border-gray-200"
            >
              <span className="text-primary-600 font-medium mr-2">
                {index + 1}.
              </span>
              <span className="text-gray-800">{topic}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Start Quiz
        </h3>
        <p className="text-gray-600 mb-4">
          Take a test to assess your knowledge. Based on your performance, 
          you'll get an adaptive follow-up quiz.
        </p>
        <button
          onClick={() => onStartQuiz('initial')}
          className="w-full bg-primary-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
        >
          Start Initial Test (15-20 MCQs)
        </button>
      </div>
    </div>
  )
}
