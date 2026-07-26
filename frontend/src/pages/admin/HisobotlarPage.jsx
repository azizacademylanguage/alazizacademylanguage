import { useState } from 'react';
import { eksportUsersCSV, eksportNatijalarCSV, importUsersCSV, eksportKontentExcel, importKontentExcel, backupYuklabOlish, backupTiklash } from '../../api/adminExtra';
import { Card, Button } from '../../components/ui';
import { Download, Upload, Users, ClipboardCheck, CheckCircle2, AlertCircle, FileSpreadsheet, Database } from 'lucide-react';

export default function HisobotlarPage() {
  const [yuklanmoqda, setYuklanmoqda] = useState('');
  const [importNatija, setImportNatija] = useState(null);
  const [importXato, setImportXato] = useState('');
  const [excelNatija, setExcelNatija] = useState(null);
  const [backupNatija, setBackupNatija] = useState(null);

  const handleExport = async (turi) => {
    setYuklanmoqda(turi);
    try {
      if (turi === 'users') await eksportUsersCSV();
      else await eksportNatijalarCSV();
    } finally {
      setYuklanmoqda('');
    }
  };

  const handleImport = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImportXato('');
    setImportNatija(null);
    try {
      const result = await importUsersCSV(file);
      setImportNatija(result);
    } catch (err) {
      setImportXato(err.response?.data?.detail || 'Import amalga oshmadi.');
    }
    e.target.value = '';
  };

  const handleBackupRestore = async (e) => {
    const file = e.target.files[0]; if (!file) return;
    if (!confirm('Backup ma\'lumotlari bazaga birlashtiriladi. Davom etasizmi?')) { e.target.value=''; return; }
    setImportXato('');
    try { setBackupNatija(await backupTiklash(file)); } catch (err) { setImportXato(err.response?.data?.detail || 'Backup tiklanmadi.'); }
    e.target.value='';
  };

  const handleContentImport = async (e) => {
    const file = e.target.files[0]; if (!file) return; setImportXato('');
    try { setExcelNatija(await importKontentExcel(file)); } catch (err) { setImportXato(err.response?.data?.detail || 'Excel import amalga oshmadi.'); }
    e.target.value = '';
  };

  return (
    <div className="animate-in">
      <h1 className="font-display text-2xl font-bold mb-1" style={{ color: 'var(--color-ink)' }}>Hisobotlar</h1>
      <p className="text-sm mb-8" style={{ color: '#8A8371' }}>Ma'lumotlarni CSV formatda yuklab oling yoki import qiling.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <Card className="p-5 animate-in-fast">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center mb-3"
            style={{ background: 'linear-gradient(135deg, var(--color-forest) 0%, var(--color-forest-light) 100%)' }}
          >
            <Users size={17} color="white" />
          </div>
          <p className="font-display font-bold text-sm mb-1" style={{ color: 'var(--color-ink)' }}>Foydalanuvchilar</p>
          <p className="text-xs mb-4" style={{ color: '#8A8371' }}>Barcha admin, nazoratchi va o'quvchilar ro'yxati.</p>
          <Button variant="secondary" onClick={() => handleExport('users')} disabled={yuklanmoqda === 'users'}>
            <Download size={14} /> {yuklanmoqda === 'users' ? 'Yuklanmoqda...' : 'CSV yuklab olish'}
          </Button>
        </Card>

        <Card className="p-5 animate-in-fast stagger-1">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center mb-3"
            style={{ background: 'linear-gradient(135deg, var(--color-amber-dark) 0%, var(--color-amber) 100%)' }}
          >
            <ClipboardCheck size={17} color="white" />
          </div>
          <p className="font-display font-bold text-sm mb-1" style={{ color: 'var(--color-ink)' }}>Mashq natijalari</p>
          <p className="text-xs mb-4" style={{ color: '#8A8371' }}>Barcha o'quvchilarning mashq natijalari (so'nggi 5000 ta).</p>
          <Button variant="secondary" onClick={() => handleExport('natijalar')} disabled={yuklanmoqda === 'natijalar'}>
            <Download size={14} /> {yuklanmoqda === 'natijalar' ? 'Yuklanmoqda...' : 'CSV yuklab olish'}
          </Button>
        </Card>
      </div>


      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        <Card className="p-5 animate-in-fast">
          <div className="flex items-center gap-2 mb-3"><FileSpreadsheet size={18} style={{ color: 'var(--color-jungle)' }} /><p className="font-display font-bold">Ta'lim kontenti Excel</p></div>
          <p className="text-xs mb-4" style={{ color: '#8A8371' }}>Mavzu, test, listening, writing va speaking ma'lumotlarini bitta XLSX faylda boshqaring.</p>
          <div className="flex flex-wrap gap-2"><Button variant="secondary" onClick={eksportKontentExcel}><Download size={14}/>XLSX yuklash</Button><label><input type="file" accept=".xlsx" hidden onChange={handleContentImport}/><span className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold cursor-pointer" style={{background:'var(--color-paper-warm)'}}><Upload size={14}/>XLSX import</span></label></div>
          {excelNatija && <div className="mt-3 text-xs p-3 rounded-xl" style={{background:'var(--color-paper-warm)'}}><b>Import:</b> {Object.entries(excelNatija.import_qilindi || {}).map(([k,v]) => `${k}: ${v}`).join(' · ')}{excelNatija.xatolar?.length > 0 && <p className="mt-2" style={{color:'var(--color-red)'}}>Xatolar: {excelNatija.xatolar.slice(0,3).join(' | ')}</p>}</div>}
        </Card>
        <Card className="p-5 animate-in-fast">
          <div className="flex items-center gap-2 mb-3"><Database size={18} style={{ color: 'var(--color-teal)' }} /><p className="font-display font-bold">Baza backup</p></div>
          <p className="text-xs mb-4" style={{ color: '#8A8371' }}>O'quvchilar, kurslar, natijalar, sertifikatlar, xaridlar va audit loglarini ZIP qilib yuklab oling.</p>
          <div className="flex flex-wrap gap-2"><Button variant="secondary" onClick={backupYuklabOlish}><Download size={14}/>Backup yuklab olish</Button><label><input type="file" accept=".zip" hidden onChange={handleBackupRestore}/><span className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold cursor-pointer" style={{background:'var(--color-paper-warm)'}}><Upload size={14}/>Backup tiklash</span></label></div>{backupNatija && <p className="text-xs mt-3" style={{color:'var(--color-forest)'}}>Tiklandi: {backupNatija.jami} qator</p>}
        </Card>
      </div>

      <Card className="p-5 animate-in-fast stagger-2">
        <div className="flex items-center gap-2 mb-3">
          <Upload size={16} style={{ color: 'var(--color-forest)' }} />
          <p className="font-display font-bold text-sm" style={{ color: 'var(--color-ink)' }}>O'quvchilarni ommaviy import qilish</p>
        </div>
        <p className="text-xs mb-4" style={{ color: '#8A8371' }}>
          CSV fayl ustunlari: <code className="px-1.5 py-0.5 rounded" style={{ background: 'var(--color-paper-warm)' }}>username,password,ism,familya</code> — har qatorda bitta o'quvchi.
        </p>
        <label>
          <input type="file" accept=".csv" hidden onChange={handleImport} />
          <span className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold cursor-pointer press" style={{ background: 'var(--color-paper-warm)', color: 'var(--color-ink)' }}>
            <Upload size={14} /> CSV faylni tanlash
          </span>
        </label>

        {importNatija && (
          <div className="mt-4 animate-pop">
            <div className="flex items-center gap-2 text-sm font-semibold mb-2" style={{ color: 'var(--color-forest)' }}>
              <CheckCircle2 size={15} /> {importNatija.yaratildi} ta o'quvchi yaratildi
            </div>
            {importNatija.xatolar?.length > 0 && (
              <div className="space-y-1">
                {importNatija.xatolar.map((x, i) => (
                  <p key={i} className="text-xs px-2 py-1 rounded flex items-center gap-1.5" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>
                    <AlertCircle size={12} /> {x}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}
        {importXato && (
          <p className="text-sm mt-3 px-3 py-2 rounded-xl" style={{ background: '#FBEAE8', color: 'var(--color-red)' }}>{importXato}</p>
        )}
      </Card>
    </div>
  );
}
