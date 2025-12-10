import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageLayout } from '../components/layout/PageLayout'
import {
    Cloud, CloudRain, CloudSnow, Sun, Wind, Droplets, Thermometer, Search,
    MapPin, Eye, Gauge, Compass, Sunrise, Sunset, Activity, Shirt,
    AlertCircle, TrendingUp, Calendar
} from 'lucide-react'

interface WeatherData {
    city: string
    country: string
    temperature: number
    feels_like: number
    temp_min: number
    temp_max: number
    description: string
    humidity: number
    pressure: number
    wind_speed: number
    wind_deg: number
    cloudiness: number
    visibility: number
    sunrise: number
    sunset: number
    timezone: number
    icon: string
}

interface ForecastDay {
    date: string
    temp_max: number
    temp_min: number
    description: string
    icon: string
}

interface AIInsights {
    analysis: string
    activities: string[]
    health_tips: string[]
    outfit_suggestions: string[]
}

export const Weather: React.FC = () => {
    const navigate = useNavigate()
    const [city, setCity] = useState('Surat')
    const [countryCode, setCountryCode] = useState('IN')
    const [searchInput, setSearchInput] = useState('')
    const [countryInput, setCountryInput] = useState('')
    const [weather, setWeather] = useState<WeatherData | null>(null)
    const [forecast, setForecast] = useState<ForecastDay[]>([])
    const [aiInsights, setAIInsights] = useState<AIInsights | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchWeather(city, countryCode)
    }, [city, countryCode])

    const fetchWeather = async (cityName: string, country?: string) => {
        setLoading(true)
        setError(null)
        try {
            const url = country
                ? `/api/v1/weather/current?city=${encodeURIComponent(cityName)}&country_code=${encodeURIComponent(country)}`
                : `/api/v1/weather/current?city=${encodeURIComponent(cityName)}`
            const response = await fetch(url)
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}))
                throw new Error(errorData.detail || 'Failed to fetch weather data')
            }
            const data = await response.json()
            setWeather(data.weather)
            setForecast(data.forecast)
            setAIInsights(data.ai_insights)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred')
            console.error('Weather fetch error:', err)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        if (searchInput.trim()) {
            setCity(searchInput.trim())
            if (countryInput.trim()) {
                setCountryCode(countryInput.trim().toUpperCase())
            }
            setSearchInput('')
            setCountryInput('')
        }
    }

    const getWeatherIcon = (iconCode: string) => {
        const code = iconCode?.toLowerCase() || ''
        if (code.includes('rain')) return CloudRain
        if (code.includes('snow')) return CloudSnow
        if (code.includes('cloud')) return Cloud
        return Sun
    }

    const getWindDirection = (deg: number) => {
        const directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        return directions[Math.round(deg / 45) % 8]
    }

    const formatTime = (timestamp: number, timezone: number) => {
        const date = new Date((timestamp + timezone) * 1000)
        return date.toUTCString().slice(-12, -7)
    }

    return (
        <PageLayout
            theme="blue"
            title="Weather Dashboard"
            subtitle="Real-time weather with AI insights"
            icon={<Cloud className="w-6 h-6 text-white" />}
            actions={
                <form onSubmit={handleSearch} className="flex gap-2">
                    <div className="relative">
                        <input
                            type="text"
                            value={searchInput}
                            onChange={(e) => setSearchInput(e.target.value)}
                            placeholder="City..."
                            className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl px-4 py-2 pl-10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50 w-40"
                        />
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/50" />
                    </div>
                    <div className="relative">
                        <input
                            type="text"
                            value={countryInput}
                            onChange={(e) => setCountryInput(e.target.value)}
                            placeholder="Country (GB, US)"
                            maxLength={2}
                            className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl px-4 py-2 pl-10 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-blue-400/50 w-44"
                        />
                        <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/50" />
                    </div>
                    <button type="submit" className="px-4 py-2 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 rounded-xl text-white font-medium transition-all">
                        Search
                    </button>
                </form>
            }
            sidePanel={
                !loading && !error && weather && aiInsights && (
                    <div className="w-96 bg-gradient-to-b from-purple-900/30 to-pink-900/30 backdrop-blur-xl border-l border-white/20 overflow-y-auto">
                        <div className="p-6 sticky top-0 bg-gradient-to-b from-purple-900/50 to-transparent backdrop-blur-xl border-b border-white/20 z-10">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2">
                                <TrendingUp className="w-6 h-6 text-purple-400" />
                                AI Insights
                            </h3>
                        </div>

                        <div className="p-6 space-y-4">
                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                <p className="text-sm text-white/90 leading-relaxed">{aiInsights.analysis}</p>
                            </div>

                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                <div className="flex items-center gap-2 mb-3">
                                    <Activity className="w-5 h-5 text-green-400" />
                                    <h4 className="font-semibold text-white">Recommended Activities</h4>
                                </div>
                                <ul className="space-y-2">
                                    {aiInsights.activities.map((activity, index) => (
                                        <li key={index} className="text-sm text-white/80 flex items-start gap-2">
                                            <span className="text-green-400 mt-1">•</span>
                                            <span>{activity}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                <div className="flex items-center gap-2 mb-3">
                                    <AlertCircle className="w-5 h-5 text-blue-400" />
                                    <h4 className="font-semibold text-white">Health & Safety</h4>
                                </div>
                                <ul className="space-y-2">
                                    {aiInsights.health_tips.map((tip, index) => (
                                        <li key={index} className="text-sm text-white/80 flex items-start gap-2">
                                            <span className="text-blue-400 mt-1">•</span>
                                            <span>{tip}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 border border-white/20">
                                <div className="flex items-center gap-2 mb-3">
                                    <Shirt className="w-5 h-5 text-pink-400" />
                                    <h4 className="font-semibold text-white">What to Wear</h4>
                                </div>
                                <ul className="space-y-2">
                                    {aiInsights.outfit_suggestions.map((outfit, index) => (
                                        <li key={index} className="text-sm text-white/80 flex items-start gap-2">
                                            <span className="text-pink-400 mt-1">•</span>
                                            <span>{outfit}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    </div>
                )
            }
        >
            <div className="space-y-6">
                {loading && (
                    <div className="text-center py-20">
                        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-400 mx-auto mb-4" />
                        <p className="text-white/70 text-lg">Loading weather data...</p>
                    </div>
                )}

                {error && (
                    <div className="bg-red-500/20 backdrop-blur-xl border border-red-500/30 rounded-2xl p-6 text-center">
                        <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-3" />
                        <p className="text-red-300 text-lg">{error}</p>
                    </div>
                )}

                {!loading && !error && weather && (
                    <>
                        {/* Current Weather Card */}
                        <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-xl rounded-3xl p-6 border border-white/20">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <MapPin className="w-5 h-5 text-blue-400" />
                                    <h2 className="text-2xl font-bold text-white">
                                        {weather.city}, {weather.country}
                                    </h2>
                                </div>
                                <p className="text-sm text-white/60">
                                    {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                                </p>
                            </div>

                            <div className="grid grid-cols-2 gap-6">
                                <div className="flex items-center gap-4">
                                    {React.createElement(getWeatherIcon(weather.icon), {
                                        className: 'w-24 h-24 text-blue-300',
                                    })}
                                    <div>
                                        <div className="text-6xl font-bold text-white">
                                            {Math.round(weather.temperature)}°
                                        </div>
                                        <p className="text-lg text-white/80 capitalize mt-1">{weather.description}</p>
                                        <p className="text-sm text-white/60">Feels like {Math.round(weather.feels_like)}°</p>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-3">
                                    <div className="bg-white/10 rounded-xl p-3">
                                        <Thermometer className="w-4 h-4 text-red-400 mb-1" />
                                        <p className="text-xs text-white/60">High/Low</p>
                                        <p className="text-lg font-bold text-white">
                                            {Math.round(weather.temp_max)}° / {Math.round(weather.temp_min)}°
                                        </p>
                                    </div>
                                    <div className="bg-white/10 rounded-xl p-3">
                                        <Droplets className="w-4 h-4 text-cyan-400 mb-1" />
                                        <p className="text-xs text-white/60">Humidity</p>
                                        <p className="text-lg font-bold text-white">{weather.humidity}%</p>
                                    </div>
                                    <div className="bg-white/10 rounded-xl p-3">
                                        <Wind className="w-4 h-4 text-blue-400 mb-1" />
                                        <p className="text-xs text-white/60">Wind</p>
                                        <p className="text-lg font-bold text-white">{Math.round(weather.wind_speed)} km/h</p>
                                    </div>
                                    <div className="bg-white/10 rounded-xl p-3">
                                        <Gauge className="w-4 h-4 text-purple-400 mb-1" />
                                        <p className="text-xs text-white/60">Pressure</p>
                                        <p className="text-lg font-bold text-white">{weather.pressure} hPa</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Additional Details */}
                        <div className="grid grid-cols-3 gap-4">
                            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 border border-white/20">
                                <div className="flex items-center gap-2 mb-3">
                                    <Eye className="w-4 h-4 text-cyan-400" />
                                    <span className="text-sm font-semibold text-white">Visibility</span>
                                </div>
                                <p className="text-2xl font-bold text-white">{weather.visibility} km</p>
                            </div>

                            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 border border-white/20">
                                <div className="flex items-center gap-2 mb-3">
                                    <Compass className="w-4 h-4 text-blue-400" />
                                    <span className="text-sm font-semibold text-white">Wind Direction</span>
                                </div>
                                <p className="text-2xl font-bold text-white">
                                    {getWindDirection(weather.wind_deg)} ({weather.wind_deg}°)
                                </p>
                            </div>

                            <div className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 border border-white/20">
                                <div className="flex items-center gap-2 mb-3">
                                    <Cloud className="w-4 h-4 text-gray-400" />
                                    <span className="text-sm font-semibold text-white">Cloudiness</span>
                                </div>
                                <p className="text-2xl font-bold text-white">{weather.cloudiness}%</p>
                            </div>
                        </div>

                        {/* Sun Times & Forecast */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div className="bg-gradient-to-br from-orange-500/20 to-yellow-500/20 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
                                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <Sunrise className="w-5 h-5 text-orange-400" />
                                    Sun Times
                                </h3>
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <Sunrise className="w-4 h-4 text-orange-300" />
                                            <span className="text-white/80">Sunrise</span>
                                        </div>
                                        <span className="text-lg font-bold text-white">
                                            {formatTime(weather.sunrise, weather.timezone)}
                                        </span>
                                    </div>
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <Sunset className="w-4 h-4 text-orange-300" />
                                            <span className="text-white/80">Sunset</span>
                                        </div>
                                        <span className="text-lg font-bold text-white">
                                            {formatTime(weather.sunset, weather.timezone)}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="md:col-span-2 bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20">
                                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                    <Calendar className="w-5 h-5 text-blue-400" />
                                    5-Day Forecast
                                </h3>
                                <div className="grid grid-cols-5 gap-3">
                                    {forecast.map((day, index) => (
                                        <div key={index} className="bg-white/5 rounded-xl p-3 text-center hover:bg-white/10 transition-colors">
                                            <p className="text-xs text-white/60 mb-2">
                                                {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}
                                            </p>
                                            {React.createElement(getWeatherIcon(day.icon), {
                                                className: 'w-8 h-8 text-blue-300 mx-auto mb-2',
                                            })}
                                            <p className="text-sm font-bold text-white">{Math.round(day.temp_max)}°</p>
                                            <p className="text-xs text-white/60">{Math.round(day.temp_min)}°</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </PageLayout>
    )
}
