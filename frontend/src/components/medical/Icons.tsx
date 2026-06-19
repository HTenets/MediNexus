export type IconProps = { className?: string };

function Svg({ className = "w-5 h-5", children }: IconProps & { children: React.ReactNode }) {
  return <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">{children}</svg>;
}

export const IconDashboard = (p: IconProps) => <Svg {...p}><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></Svg>;
export const IconBrain = (p: IconProps) => <Svg {...p}><path d="M9.663 17h4.673M12 3v1m6.364 1.636-.707.707M21 12h-1M4 12H3m3.343-5.657-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/></Svg>;
export const IconFile = (p: IconProps) => <Svg {...p}><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></Svg>;
export const IconUser = (p: IconProps) => <Svg {...p}><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></Svg>;
export const IconBell = (p: IconProps) => <Svg {...p}><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></Svg>;
export const IconHeart = (p: IconProps) => <Svg {...p}><path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/></Svg>;
export const IconChart = (p: IconProps) => <Svg {...p}><path d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9"/><path d="M6 20.25h12A2.25 2.25 0 0020.25 18V6A2.25 2.25 0 0018 3.75H6A2.25 2.25 0 003.75 6v12A2.25 2.25 0 006 20.25z"/></Svg>;
export const IconCheck = (p: IconProps) => <Svg {...p}><path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></Svg>;
export const IconAlert = (p: IconProps) => <Svg {...p}><path d="M12 9v3.75m0 3.75h.007M2.697 16.126L10.05 3.378c.866-1.5 3.032-1.5 3.898 0l7.355 12.748c.866 1.5-.217 3.374-1.948 3.374H4.645c-1.73 0-2.813-1.874-1.948-3.374z"/></Svg>;
export const IconBook = (p: IconProps) => <Svg {...p}><path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"/></Svg>;
export const IconExternal = (p: IconProps) => <Svg {...p}><path d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></Svg>;
export const IconChevron = (p: IconProps) => <Svg {...p}><path d="M8.25 4.5l7.5 7.5-7.5 7.5"/></Svg>;
export const IconPhone = (p: IconProps) => <Svg {...p}><path d="M22 16.92v3a2 2 0 01-2.18 2A19.79 19.79 0 0111.19 18.9 19.5 19.5 0 015.1 12.81 19.79 19.79 0 012.08 4.18 2 2 0 014.06 2h3a2 2 0 012 1.72c.13.97.37 1.91.72 2.81a2 2 0 01-.45 2.11L8.05 9.92a16 16 0 006.03 6.03l1.27-1.27a2 2 0 012.11-.45c.9.35 1.84.59 2.81.72A2 2 0 0122 16.92z"/></Svg>;
export const IconUpload = (p: IconProps) => <Svg {...p}><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></Svg>;
export const IconSettings = (p: IconProps) => <Svg {...p}><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06A1.65 1.65 0 0015 19.4a1.65 1.65 0 00-1 .6 1.65 1.65 0 00-.33 1.82V22a2 2 0 01-4 0v-.09A1.65 1.65 0 009 20.6a1.65 1.65 0 00-1-.6 1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.6 15a1.65 1.65 0 00-.6-1 1.65 1.65 0 00-1.82-.33H2a2 2 0 010-4h.09A1.65 1.65 0 003.4 9a1.65 1.65 0 00.6-1 1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.6a1.65 1.65 0 001-.6 1.65 1.65 0 00.33-1.82V2a2 2 0 014 0v.09A1.65 1.65 0 0015 3.4a1.65 1.65 0 001 .6 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9c.24.36.45.73.6 1.15H22a2 2 0 010 4h-.09A1.65 1.65 0 0019.4 15z"/></Svg>;
