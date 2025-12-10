import React, { useState, useEffect, memo } from 'react'

interface TypewriterProps {
    text: string
    speed?: number
    onComplete?: () => void
    onUpdate?: () => void
}

export const Typewriter: React.FC<TypewriterProps> = memo(
    ({ text, speed = 10, onComplete, onUpdate }) => {
        const [displayedText, setDisplayedText] = useState('')

        useEffect(() => {
            let index = 0
            setDisplayedText('') // Reset when text changes (or initial)

            // If text is empty, just return
            if (!text) return

            const intervalId = setInterval(() => {
                const nextText = text.slice(0, index + 1)
                setDisplayedText(nextText)
                if (onUpdate) onUpdate()
                index++
                if (index > text.length) {
                    clearInterval(intervalId)
                    if (onComplete) onComplete()
                }
            }, speed)

            return () => clearInterval(intervalId)
        }, [text, speed, onComplete])

        // If text is already fully displayed from a previous render (e.g. strict mode or re-parenting),
        // we might want to ensure it stays consistent, but this effect resets it.
        // For chat history, we generally want to show full text immediately, so this component
        // should ONLY be used for the *latest* active message.

        return (
            <span className="whitespace-pre-wrap break-words">
                {displayedText}
            </span>
        )
    }
)
