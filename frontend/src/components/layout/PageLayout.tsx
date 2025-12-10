import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Home } from 'lucide-react';
import WebGLBackground from '../webGL/WebGLBackground';

interface PageLayoutProps {
  children: React.ReactNode;
  theme: 'purple' | 'blue' | 'indigo' | 'slate';
  title: string | React.ReactNode;
  subtitle?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  sidePanel?: React.ReactNode;
  showHomeButton?: boolean;
  maxWidth?: '6xl' | '7xl' | 'full';
}

export const PageLayout: React.FC<PageLayoutProps> = ({
  children,
  theme,
  title,
  subtitle,
  icon,
  actions,
  sidePanel,
  showHomeButton = true,
  maxWidth = '7xl'
}) => {
  const navigate = useNavigate();

  // Theme configuration
  const themeConfig = {
    purple: {
      bg: 'from-slate-900 via-purple-900 to-slate-900',
      overlay: 'from-purple-900/20 via-transparent to-blue-900/20',
      iconBg: 'from-purple-500 to-pink-500',
      titleGradient: 'from-purple-400 via-pink-400 to-blue-400',
    },
    blue: {
      bg: 'from-slate-900 via-blue-900 to-slate-900',
      overlay: 'from-blue-900/20 via-transparent to-purple-900/20',
      iconBg: 'from-blue-500 to-cyan-500',
      titleGradient: 'from-blue-400 via-cyan-400 to-purple-400',
    },
    indigo: {
      bg: 'from-slate-900 via-indigo-900 to-slate-900',
      overlay: 'from-indigo-900/20 via-transparent to-purple-900/20',
      iconBg: 'from-purple-500 to-indigo-500',
      titleGradient: 'from-purple-400 via-pink-400 to-indigo-400',
    },
    slate: {
      bg: 'from-slate-900 via-slate-800 to-slate-900',
      overlay: 'from-slate-900/20 via-transparent to-gray-900/20',
      iconBg: 'from-slate-500 to-gray-500',
      titleGradient: 'from-white via-slate-200 to-gray-400',
    }
  };

  const currentTheme = themeConfig[theme];

  return (
    <div className={`min-h-screen flex overflow-hidden relative bg-gradient-to-br ${currentTheme.bg}`}>
      <WebGLBackground 
          particleCount={1200}
          className="fixed inset-0 w-full h-full opacity-30"
          shaderName="particles"
          shape="sphere"
      />
      <div className={`fixed inset-0 bg-gradient-to-br ${currentTheme.overlay} pointer-events-none`} />

      <div className="flex-1 flex relative z-10">
          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-y-auto">
              {/* Header */}
              <div className="bg-white/10 backdrop-blur-xl border-b border-white/20 px-6 py-4 sticky top-0 z-20 shadow-lg">
                  <div className={`mx-auto flex items-center justify-between ${maxWidth === 'full' ? 'w-full' : `max-w-${maxWidth}`}`}>
                      <div className="flex items-center gap-4">
                          {showHomeButton && (
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                                title="Go to Dashboard"
                            >
                                <Home className="w-6 h-6 text-white/80" />
                            </button>
                          )}
                          
                          {icon && (
                            <div className={`p-2 bg-gradient-to-br ${currentTheme.iconBg} rounded-xl shadow-lg`}>
                                {icon}
                            </div>
                          )}
                          
                          <div>
                              <h1 className={`text-2xl font-bold bg-gradient-to-r ${currentTheme.titleGradient} bg-clip-text text-transparent`}>
                                  {title}
                              </h1>
                              {subtitle && <p className="text-white/70 text-sm">{subtitle}</p>}
                          </div>
                      </div>

                      {actions && (
                        <div className="flex items-center gap-3">
                          {actions}
                        </div>
                      )}
                  </div>
              </div>

              {/* Content Area */}
              <div className="flex-1 p-6">
                  <div className={`mx-auto ${maxWidth === 'full' ? 'w-full' : `max-w-${maxWidth}`}`}>
                      {children}
                  </div>
              </div>
          </div>

          {/* Right Side Panel */}
          {sidePanel}
      </div>
    </div>
  );
};
