export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex-1 h-full overflow-y-auto bg-[#FAF9F6]">
      {children}
    </div>
  );
}
