import React, { useEffect, useRef, useState } from 'react'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'

interface VectorVisualizationProps {
    data: {
        points: number[][]
        labels: string[]
        metadata?: Record<string, unknown>[]
        total_points: number
    } | null
    className?: string
}

const VectorVisualization: React.FC<VectorVisualizationProps> = ({
    data,
    className = 'w-full h-96 bg-slate-900 rounded-lg',
}) => {
    const mountRef = useRef<HTMLDivElement>(null)
    const sceneRef = useRef<THREE.Scene | null>(null)
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null)
    const controlsRef = useRef<OrbitControls | null>(null)
    const animationIdRef = useRef<number | null>(null)
    const [hasError, setHasError] = useState(false)

    useEffect(() => {
        if (!mountRef.current || !data || data.points.length === 0) {
            return
        }

        const initThreeJS = () => {
            try {
                setHasError(false)
                const mount = mountRef.current!
                const width = mount.clientWidth
                const height = mount.clientHeight

                // Scene with gradient-like dark background
                const scene = new THREE.Scene()
                scene.background = new THREE.Color(0x1a1a2e) // dark blue-gray for depth
                sceneRef.current = scene

                // Camera - positioned to view the scaled data
                const camera = new THREE.PerspectiveCamera(
                    75,
                    width / height,
                    0.1,
                    1000
                )
                camera.position.set(4, 4, 4) // Further back to see all scaled points
                camera.lookAt(0, 0, 0) // Look at center

                // Renderer
                const renderer = new THREE.WebGLRenderer({
                    antialias: true,
                    alpha: false,
                })
                renderer.setSize(width, height)
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
                renderer.setClearColor(0x1a1a2e, 1) // Match background
                mount.appendChild(renderer.domElement)
                rendererRef.current = renderer

                // Controls
                const controls = new OrbitControls(camera, renderer.domElement)
                controls.enableDamping = true
                controls.dampingFactor = 0.05
                controlsRef.current = controls

                // Create points with scaling to fit in view
                const geometry = new THREE.BufferGeometry()

                // Scale points to fit within reasonable bounds (-2 to 2 range)
                const scaledPoints = data.points.map((point) => {
                    const scale = 2.0 // Scale factor to fit in view
                    return [
                        point[0] * scale,
                        point[1] * scale,
                        point[2] * scale,
                    ]
                })

                const positions = new Float32Array(scaledPoints.flat())
                geometry.setAttribute(
                    'position',
                    new THREE.BufferAttribute(positions, 3)
                )

                // Colors - create gradient colors for points
                const colors = new Float32Array(data.points.length * 3)
                for (let i = 0; i < data.points.length; i++) {
                    const t = i / (data.points.length - 1) // Normalized position 0-1

                    // Create vibrant gradient: purple -> blue -> cyan -> green -> yellow -> red
                    let r, g, b
                    if (t < 0.2) {
                        // Purple to blue
                        const tt = t / 0.2
                        r = 0.7 + (0.3 - 0.7) * tt
                        g = 0.3 + (0.5 - 0.3) * tt
                        b = 1.0
                    } else if (t < 0.4) {
                        // Blue to cyan
                        const tt = (t - 0.2) / 0.2
                        r = 0.3 + (0.2 - 0.3) * tt
                        g = 0.5 + (0.9 - 0.5) * tt
                        b = 1.0
                    } else if (t < 0.6) {
                        // Cyan to green
                        const tt = (t - 0.4) / 0.2
                        r = 0.2
                        g = 0.9 + (0.8 - 0.9) * tt
                        b = 1.0 + (0.4 - 1.0) * tt
                    } else if (t < 0.8) {
                        // Green to yellow
                        const tt = (t - 0.6) / 0.2
                        r = 0.2 + (1.0 - 0.2) * tt
                        g = 0.8 + (1.0 - 0.8) * tt
                        b = 0.4 + (0.5 - 0.4) * tt
                    } else {
                        // Yellow to red
                        const tt = (t - 0.8) / 0.2
                        r = 1.0
                        g = 1.0 + (0.3 - 1.0) * tt
                        b = 0.5 + (0.3 - 0.5) * tt
                    }

                    colors[i * 3] = r
                    colors[i * 3 + 1] = g
                    colors[i * 3 + 2] = b
                }
                geometry.setAttribute(
                    'color',
                    new THREE.BufferAttribute(colors, 3)
                )

                // Material - large, bright dots
                const material = new THREE.PointsMaterial({
                    size: 0.1,
                    vertexColors: true,
                    transparent: true,
                    opacity: 1.0,
                    sizeAttenuation: true,
                })

                // Points mesh
                const points = new THREE.Points(geometry, material)
                scene.add(points)

                // Add axes helper - scaled for visibility
                const axesHelper = new THREE.AxesHelper(2.5)
                scene.add(axesHelper)

                // Scene initialized

                // Animation loop with smooth auto-rotation
                let lastTime = performance.now()
                const animate = (currentTime: number) => {
                    animationIdRef.current = requestAnimationFrame(animate)

                    // Calculate delta time for smooth animation
                    const deltaTime = (currentTime - lastTime) / 1000 // Convert to seconds
                    lastTime = currentTime

                    controls.update()

                    // Auto-rotate the points with delta time for smooth animation
                    if (points) {
                        const rotationSpeed = 0.5 // Base rotation speed (radians per second)
                        points.rotation.y += rotationSpeed * deltaTime
                        points.rotation.x += rotationSpeed * deltaTime * 0.5 // Slower X rotation
                    }

                    renderer.render(scene, camera)
                }
                // Start the animation loop
                animationIdRef.current = requestAnimationFrame(animate)
            } catch (error) {
                console.error(
                    'VectorVisualization: Failed to initialize Three.js:',
                    error
                )
                setHasError(true)
            }
        }

        const cleanup = () => {
            if (animationIdRef.current) {
                cancelAnimationFrame(animationIdRef.current)
                animationIdRef.current = null
            }

            if (controlsRef.current) {
                controlsRef.current.dispose()
                controlsRef.current = null
            }

            if (rendererRef.current && mountRef.current) {
                mountRef.current.removeChild(rendererRef.current.domElement)
                rendererRef.current.dispose()
                rendererRef.current = null
            }

            if (sceneRef.current) {
                // Dispose of geometries and materials
                sceneRef.current.traverse((object) => {
                    if (
                        object instanceof THREE.Mesh ||
                        object instanceof THREE.Points
                    ) {
                        if (object.geometry) object.geometry.dispose()
                        if (object.material) {
                            if (Array.isArray(object.material)) {
                                object.material.forEach((material) =>
                                    material.dispose()
                                )
                            } else {
                                object.material.dispose()
                            }
                        }
                    }
                })
                sceneRef.current = null
            }

            // Scene cleaned up
        }

        // Cleanup previous instance
        cleanup()

        // Initialize new instance
        initThreeJS()

        // Handle window resize
        const handleResize = () => {
            if (!rendererRef.current || !sceneRef.current || !mountRef.current)
                return

            const camera = sceneRef.current.children.find(
                (child) => child instanceof THREE.Camera
            ) as THREE.PerspectiveCamera
            if (!camera) return

            const width = mountRef.current.clientWidth
            const height = mountRef.current.clientHeight

            camera.aspect = width / height
            camera.updateProjectionMatrix()

            rendererRef.current.setSize(width, height)
        }

        // Initial resize to ensure proper sizing
        setTimeout(handleResize, 100)

        window.addEventListener('resize', handleResize)

        return () => {
            window.removeEventListener('resize', handleResize)
            cleanup()
        }
    }, [data])

    if (!data || data.points.length === 0) {
        return (
            <div
                className={`${className} flex items-center justify-center text-white/60`}
            >
                <div className="text-center">
                    <div className="text-4xl mb-4">📊</div>
                    <p>No vector data available</p>
                    <p className="text-sm mt-2">
                        Upload and process documents to see 3D visualization
                    </p>
                </div>
            </div>
        )
    }

    if (hasError) {
        return (
            <div
                className={`${className} flex items-center justify-center text-red-400`}
            >
                <div className="text-center">
                    <div className="text-4xl mb-4">⚠️</div>
                    <p>Failed to load 3D visualization</p>
                    <p className="text-sm mt-2">WebGL may not be supported</p>
                </div>
            </div>
        )
    }

    return (
        <div className={className}>
            <div
                ref={mountRef}
                className="w-full h-full overflow-hidden bg-slate-900"
                style={{
                    position: 'relative',
                    width: '100%',
                    height: '100%',
                    minHeight: '400px',
                }}
            />
            <div className="mt-2 text-xs text-white/60 text-center">
                {data.total_points} vectors • Auto-rotating • Use mouse to
                interact • Axes: Red=X, Green=Y, Blue=Z
            </div>
        </div>
    )
}

export default VectorVisualization
