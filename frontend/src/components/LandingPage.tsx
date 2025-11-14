/**
 * Beautiful Landing Page Component
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  Shield,
  DollarSign,
  Zap,
  Eye,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Lock,
  Database,
  Clock,
  Target,
  ArrowRight,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden px-4 py-20 sm:px-6 lg:px-8">
        <div className="absolute inset-0 -z-10">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10" />
          <div className="absolute left-1/2 top-0 -translate-x-1/2 blur-3xl">
            <div className="h-96 w-96 rounded-full bg-gradient-to-r from-blue-400 to-purple-400 opacity-20" />
          </div>
        </div>

        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            <div className="mb-6 inline-flex items-center rounded-full bg-blue-100 px-6 py-2 text-sm font-semibold text-blue-700">
              <Zap className="mr-2 h-4 w-4" />
              Production-Ready Observability Platform
            </div>

            <h1 className="mb-6 text-5xl font-bold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl">
              Complete Visibility Into
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {' '}Your LLM System
              </span>
            </h1>

            <p className="mx-auto mb-10 max-w-3xl text-xl text-gray-600 sm:text-2xl">
              Track every API call, monitor costs in real-time, and ensure your LLM
              infrastructure runs smoothly with comprehensive observability.
            </p>

            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <button
                onClick={() => navigate('/dashboard')}
                className="group inline-flex items-center rounded-full bg-gradient-to-r from-blue-600 to-purple-600 px-8 py-4 text-lg font-semibold text-white shadow-lg transition-all hover:scale-105 hover:shadow-xl"
              >
                View Dashboard
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </button>

              <button
                onClick={() => document.getElementById('benefits')?.scrollIntoView({ behavior: 'smooth' })}
                className="inline-flex items-center rounded-full border-2 border-gray-300 bg-white px-8 py-4 text-lg font-semibold text-gray-700 transition-all hover:border-blue-600 hover:text-blue-600"
              >
                Learn More
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="mt-20 grid grid-cols-2 gap-8 sm:grid-cols-4">
            {[
              { icon: Activity, label: 'Real-Time Tracking', value: '< 5ms' },
              { icon: DollarSign, label: 'Cost Savings', value: 'Up to 68%' },
              { icon: Eye, label: 'Full Visibility', value: '100%' },
              { icon: Shield, label: 'Security Layers', value: '4' },
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <div className="mb-3 inline-flex items-center justify-center rounded-2xl bg-white p-4 shadow-lg">
                  <stat.icon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why This Platform Matters */}
      <section className="bg-white px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900">
              Why LLM Observability Matters
            </h2>
            <p className="mx-auto mb-16 max-w-3xl text-xl text-gray-600">
              In production LLM systems, blind spots lead to overspending,
              security vulnerabilities, and degraded user experience.
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                icon: Target,
                title: 'Mission Critical',
                description: 'LLM applications are now critical infrastructure. Downtime or performance issues directly impact your users and revenue.',
                color: 'blue',
              },
              {
                icon: DollarSign,
                title: 'Cost Control',
                description: 'Without tracking, LLM costs can spiral out of control. One inefficient prompt can cost thousands in a high-traffic system.',
                color: 'green',
              },
              {
                icon: Shield,
                title: 'Security & Compliance',
                description: 'Track security events, PII exposure, and ensure your 4-layer security system is functioning correctly at all times.',
                color: 'purple',
              },
            ].map((item, index) => (
              <div
                key={index}
                className="group rounded-2xl border-2 border-gray-200 bg-white p-8 transition-all hover:border-blue-400 hover:shadow-xl"
              >
                <div className={`mb-4 inline-flex rounded-xl bg-${item.color}-100 p-3`}>
                  <item.icon className={`h-8 w-8 text-${item.color}-600`} />
                </div>
                <h3 className="mb-3 text-xl font-bold text-gray-900">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section id="benefits" className="bg-gradient-to-br from-blue-50 to-purple-50 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900">
              Powerful Benefits for Your Team
            </h2>
            <p className="mx-auto mb-16 max-w-3xl text-xl text-gray-600">
              Transform how you monitor, optimize, and secure your LLM infrastructure
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: Clock,
                title: 'Real-Time Monitoring',
                description: 'Track every API call with millisecond precision. Auto-refreshing dashboard shows live request feed.',
                benefits: ['< 5ms overhead', 'Auto-refresh every 5s', 'Live request feed'],
              },
              {
                icon: DollarSign,
                title: 'Cost Optimization',
                description: 'Automatic cost calculation per request. See which models cost the most and optimize spending.',
                benefits: ['Per-request costs', 'Model breakdown', 'Savings tracking'],
              },
              {
                icon: TrendingUp,
                title: 'Performance Analytics',
                description: 'Track latency (avg + P95), TTFT, tokens/second, and error rates across all models.',
                benefits: ['Latency tracking', 'Token metrics', 'Error analysis'],
              },
              {
                icon: Shield,
                title: 'Security Integration',
                description: 'Monitor your 4-layer security system: Llama Guard, RBAC, NeMo Guardrails, PII Firewall.',
                benefits: ['Security events', 'Threat detection', 'PII tracking'],
              },
              {
                icon: Database,
                title: 'Cache Analytics',
                description: 'Track cache hit rates and see cost savings from semantic caching in real-time.',
                benefits: ['Hit/miss rates', 'Cost savings', 'Performance gains'],
              },
              {
                icon: BarChart3,
                title: 'AI Router Insights',
                description: 'See which models were selected by your AI router and how much cost was saved.',
                benefits: ['Model selection', 'Cost comparison', 'Routing efficiency'],
              },
            ].map((benefit, index) => (
              <div
                key={index}
                className="rounded-2xl border-2 border-white bg-white p-6 shadow-lg transition-all hover:scale-105 hover:shadow-2xl"
              >
                <div className="mb-4 inline-flex rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 p-3">
                  <benefit.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="mb-2 text-xl font-bold text-gray-900">{benefit.title}</h3>
                <p className="mb-4 text-gray-600">{benefit.description}</p>
                <ul className="space-y-2">
                  {benefit.benefits.map((item, i) => (
                    <li key={i} className="flex items-center text-sm text-gray-700">
                      <CheckCircle className="mr-2 h-4 w-4 text-green-600" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Problems Avoided Section */}
      <section className="bg-white px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl">
          <div className="text-center">
            <h2 className="mb-4 text-4xl font-bold text-gray-900">
              Critical Problems We Help You Avoid
            </h2>
            <p className="mx-auto mb-16 max-w-3xl text-xl text-gray-600">
              Don't let these common issues derail your LLM application
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2">
            {[
              {
                icon: AlertTriangle,
                problem: 'Unexpected Cost Explosions',
                solution: 'Track costs per request and get alerted when spending spikes',
                impact: 'Teams waste thousands on inefficient prompts',
                color: 'red',
              },
              {
                icon: Clock,
                problem: 'Performance Degradation',
                solution: 'Monitor latency trends and identify slow models instantly',
                impact: 'Users abandon slow applications',
                color: 'orange',
              },
              {
                icon: Shield,
                problem: 'Security Blind Spots',
                solution: 'Track all security layer events and PII exposures',
                impact: 'Data breaches and compliance violations',
                color: 'red',
              },
              {
                icon: Target,
                problem: 'Model Selection Mistakes',
                solution: 'See AI router decisions and optimize model usage',
                impact: 'Overpaying for models you don\'t need',
                color: 'yellow',
              },
              {
                icon: Database,
                problem: 'Cache Inefficiency',
                solution: 'Monitor cache hit rates and identify opportunities',
                impact: 'Wasted API calls and increased costs',
                color: 'purple',
              },
              {
                icon: Activity,
                problem: 'Hidden Errors',
                solution: 'Track error rates and categorize failures',
                impact: 'Silent failures hurting user experience',
                color: 'red',
              },
            ].map((item, index) => (
              <div
                key={index}
                className="group rounded-2xl border-2 border-gray-200 bg-gradient-to-br from-white to-gray-50 p-8 transition-all hover:border-red-400 hover:shadow-xl"
              >
                <div className="mb-4 flex items-start justify-between">
                  <div className={`rounded-xl bg-${item.color}-100 p-3`}>
                    <item.icon className={`h-6 w-6 text-${item.color}-600`} />
                  </div>
                  <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
                    CRITICAL
                  </span>
                </div>
                <h3 className="mb-2 text-xl font-bold text-gray-900">{item.problem}</h3>
                <p className="mb-4 text-sm text-gray-600">
                  <span className="font-semibold text-red-600">Without tracking: </span>
                  {item.impact}
                </p>
                <div className="rounded-lg border-l-4 border-green-600 bg-green-50 p-4">
                  <p className="text-sm font-semibold text-green-900">Our Solution:</p>
                  <p className="text-sm text-green-700">{item.solution}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-20 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h2 className="mb-6 text-4xl font-bold text-white sm:text-5xl">
            Ready to Take Control of Your LLM Infrastructure?
          </h2>
          <p className="mb-10 text-xl text-blue-100">
            Start monitoring your LLM system in minutes. See exactly what's happening,
            optimize costs, and ensure security compliance.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <button
              onClick={() => navigate('/dashboard')}
              className="group inline-flex items-center rounded-full bg-white px-8 py-4 text-lg font-semibold text-blue-600 shadow-lg transition-all hover:scale-105 hover:shadow-2xl"
            >
              Open Dashboard
              <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </div>
      </section>

      {/* Thank You Section */}
      <section className="bg-white px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex rounded-full bg-gradient-to-r from-blue-600 to-purple-600 p-1">
            <div className="rounded-full bg-white px-8 py-3">
              <p className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-lg font-bold text-transparent">
                Thank You
              </p>
            </div>
          </div>
          <h3 className="mb-4 text-3xl font-bold text-gray-900">
            Thank You for Choosing Our Platform
          </h3>
          <p className="text-lg text-gray-600">
            We're committed to helping you build better, more reliable LLM applications.
            Your success is our mission. If you have any questions or need support,
            we're here to help every step of the way.
          </p>
          <div className="mt-8 flex items-center justify-center gap-8">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">24/7</div>
              <div className="text-sm text-gray-600">Support</div>
            </div>
            <div className="h-12 w-px bg-gray-300" />
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">99.9%</div>
              <div className="text-sm text-gray-600">Uptime</div>
            </div>
            <div className="h-12 w-px bg-gray-300" />
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">< 5ms</div>
              <div className="text-sm text-gray-600">Overhead</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
