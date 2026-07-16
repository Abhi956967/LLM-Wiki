import { describe, expect, it } from 'vitest'

import { extractTocFromMarkdown, stripLegacyQuizWrapper } from './WikiContent'

describe('extractTocFromMarkdown quiz terminology', () => {
  it('displays a legacy Checkpoint heading as Quiz without changing its anchor', () => {
    expect(extractTocFromMarkdown('## Checkpoint\n\n### Review')).toEqual([
      { id: 'checkpoint', text: 'Quiz', level: 2 },
      { id: 'review', text: 'Review', level: 3 },
    ])
  })

  it('removes the redundant generated wrapper directly around a quiz', () => {
    const content = `## Checkpoint

Try to answer without looking back.

\`\`\`quiz
questions:
  - prompt: Question?
    options: [One, Two]
    answer: 0
\`\`\`
`
    const normalized = stripLegacyQuizWrapper(content)

    expect(normalized).not.toContain('Checkpoint')
    expect(normalized).not.toContain('Try to answer without looking back.')
    expect(normalized).toContain('```quiz')
    expect(extractTocFromMarkdown(normalized)).toEqual([])
  })
})
