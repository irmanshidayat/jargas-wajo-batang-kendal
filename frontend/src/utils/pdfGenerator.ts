import jsPDF from 'jspdf'
// @ts-ignore - jspdf-autotable doesn't have proper TypeScript definitions
import autoTable from 'jspdf-autotable'
import logoImage from '@/assets/images/Logo_KSM.png'

/**
 * Convert image to base64 string
 */
const imageToBase64 = (imageUrl: string): Promise<string> => {
  return new Promise((resolve, reject) => {
    // Try fetch first (for imported images in Vite)
    fetch(imageUrl)
      .then(response => response.blob())
      .then(blob => {
        const reader = new FileReader()
        reader.onloadend = () => {
          const base64 = reader.result as string
          resolve(base64)
        }
        reader.onerror = reject
        reader.readAsDataURL(blob)
      })
      .catch(() => {
        // Fallback to Image method if fetch fails
        const img = new Image()
        img.crossOrigin = 'anonymous'
        img.onload = () => {
          const canvas = document.createElement('canvas')
          canvas.width = img.width
          canvas.height = img.height
          const ctx = canvas.getContext('2d')
          if (!ctx) {
            reject(new Error('Could not get canvas context'))
            return
          }
          ctx.drawImage(img, 0, 0)
          try {
            const base64 = canvas.toDataURL('image/png')
            resolve(base64)
          } catch (error) {
            reject(error)
          }
        }
        img.onerror = reject
        img.src = imageUrl
      })
  })
}

export interface SuratPermintaanItem {
  no: number
  kodeBarang: string
  namaBarang: string
  qty: string
  sat: string
  sumberBarang: {
    proyek: boolean
    proyekValue?: string
    stok: boolean
    stokValue?: string
  }
  peruntukan: {
    proyek: boolean
    proyekValue?: string
    produksi: boolean
    produksiValue?: string
    kantor: boolean
    lainLain: boolean
  }
}

export interface SuratPermintaanData {
  tanggal: string
  items: SuratPermintaanItem[]
  signatures: {
    pemohon?: string
    menyetujui?: string
    yangMenyerahkan?: string
    mengetahuiSPV?: string
    mengetahuiAdminGudang?: string
  }
}

export interface SuratJalanItem {
  no: number
  namaBarang: string
  qty: number
  ket?: string
}

export interface SuratJalanData {
  nomorForm: string
  kepada: string
  tanggalPengiriman: string
  items: SuratJalanItem[]
  namaPemberi?: string
  namaPenerima?: string
  tanggalDiterima?: string
}

/**
 * Format date dari YYYY-MM-DD ke DD/MM/YYYY
 */
const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  const [year, month, day] = dateStr.split('-')
  return `${day}/${month}/${year}`
}

/**
 * Generate PDF untuk Surat Permintaan
 */
export const generateSuratPermintaanPDF = async (data: SuratPermintaanData): Promise<void> => {
  const doc = new jsPDF('p', 'mm', 'a4')
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 15
  let yPos = margin

  // Set font
  doc.setFontSize(10)

  // Header Section - Load and add logo
  try {
    const logoBase64 = await imageToBase64(logoImage)
    // Add logo with appropriate size (logo height sekitar 20mm)
    const logoWidth = 30
    const logoHeight = 15
    doc.addImage(logoBase64, 'PNG', margin, yPos, logoWidth, logoHeight)
    yPos = yPos + logoHeight + 5 // Adjust yPos after logo
  } catch (error) {
    console.error('Error loading logo:', error)
    // Fallback to text if logo fails to load
    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    doc.text('PT Kian Santang Muliatama Tbk', margin, yPos + 10)
    yPos = yPos + 10
  }

  // Document info (top right) - pastikan tidak overlap dengan logo
  doc.setFontSize(8)
  const docInfoX = pageWidth - margin - 50
  const docInfoY = margin
  doc.text('No. Dok: FM-KSM-WH-08', docInfoX, docInfoY)
  doc.text('Revisi: 00', docInfoX, docInfoY + 5)
  doc.text('Tgl Efektif: 28/01/2019', docInfoX, docInfoY + 10)
  doc.text('Halaman: Page 1 of 1', docInfoX, docInfoY + 15)

  // Title - beri jarak lebih jauh dari header untuk menghindari overlap
  yPos = Math.max(yPos, 35) // Ensure minimum spacing
  doc.setFontSize(14)
  doc.setFont('helvetica', 'bold')
  doc.text('PERMOHONAN PENGAMBILAN BARANG', margin, yPos, {
    align: 'left'
  })

  // Tanggal
  yPos = yPos + 10
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('Tanggal:', margin, yPos)
  doc.text(formatDate(data.tanggal), margin + 25, yPos)

  // Table Section - beri jarak dari tanggal
  yPos = yPos + 8

  // Prepare table data
  const tableData = data.items.map((item) => {
    // Format sumber barang
    const sumberBarangParts: string[] = []
    if (item.sumberBarang.proyek) {
      sumberBarangParts.push(`Proyek: ${item.sumberBarang.proyekValue || ''}`)
    }
    if (item.sumberBarang.stok) {
      sumberBarangParts.push(item.sumberBarang.stokValue ? `Stok: ${item.sumberBarang.stokValue}` : 'Stok')
    }
    const sumberBarang = sumberBarangParts.join(', ')

    // Format peruntukan
    const peruntukanParts: string[] = []
    if (item.peruntukan.proyek) {
      peruntukanParts.push(`Proyek: ${item.peruntukan.proyekValue || ''}`)
    }
    if (item.peruntukan.produksi) {
      peruntukanParts.push(`Produksi: ${item.peruntukan.produksiValue || ''}`)
    }
    if (item.peruntukan.kantor) {
      peruntukanParts.push('Kantor')
    }
    if (item.peruntukan.lainLain) {
      peruntukanParts.push('Lain-lain')
    }
    const peruntukan = peruntukanParts.join(', ')

    // Format qty to preserve decimal values (e.g., 1.2 instead of 1)
    // Use toFixed(2) to ensure 2 decimal places, then remove trailing zeros for cleaner display
    const qtyFormatted = item.qty 
      ? (() => {
          const num = typeof item.qty === 'number' ? item.qty : parseFloat(item.qty.toString())
          return num.toFixed(2).replace(/\.?0+$/, '')
        })()
      : ''
    
    return [
      item.no.toString(),
      item.kodeBarang || '',
      item.namaBarang || '',
      qtyFormatted,
      item.sat || '',
      sumberBarang,
      peruntukan || ''
    ]
  })

  autoTable(doc, {
    startY: yPos,
    head: [
      [
        'NO.',
        'KODE BARANG',
        'NAMA BARANG',
        'QTY',
        'SAT.',
        'SUMBER BARANG (Acc.)',
        'PERUNTUKAN'
      ]
    ],
    body: tableData,
    theme: 'grid',
    headStyles: {
      fillColor: [255, 255, 255],
      textColor: [0, 0, 0],
      fontStyle: 'bold',
      fontSize: 8,
      halign: 'center'
    },
    bodyStyles: {
      fontSize: 8,
      cellPadding: 2
    },
    columnStyles: {
      0: { cellWidth: 10, halign: 'center' }, // NO
      1: { cellWidth: 25, halign: 'left' }, // KODE BARANG
      2: { cellWidth: 35, halign: 'left' }, // NAMA BARANG
      3: { cellWidth: 15, halign: 'center' }, // QTY
      4: { cellWidth: 15, halign: 'center' }, // SAT
      5: { cellWidth: 35, halign: 'left' }, // SUMBER BARANG
      6: { cellWidth: 40, halign: 'left' } // PERUNTUKAN
    },
    styles: {
      lineWidth: 0.1,
      lineColor: [0, 0, 0]
    },
    margin: { left: margin, right: margin }
  })

  // Get final Y position after table
  const finalY = (doc as any).lastAutoTable.finalY || yPos + 100

  // Footer Section (Signatures)
  yPos = finalY + 15

  // Signature columns
  const signatureWidth = (pageWidth - 2 * margin) / 5
  const signatureLabels = [
    'Pemohon\n(Mandor)',
    'Menyetujui\n(PIC)',
    'Yang Menyerahkan',
    'Mengetahui\n(SPV)',
    'Mengetahui\nAdmin Gudang'
  ]

  const signatureValues = [
    data.signatures.pemohon || '',
    data.signatures.menyetujui || '',
    data.signatures.yangMenyerahkan || '',
    data.signatures.mengetahuiSPV || '',
    data.signatures.mengetahuiAdminGudang || ''
  ]

  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')

  for (let i = 0; i < 5; i++) {
    const xPos = margin + i * signatureWidth
    const labelY = yPos
    const valueY = yPos + 25
    const lineY = yPos + 20

    // Label
    doc.text(signatureLabels[i], xPos + signatureWidth / 2, labelY, {
      align: 'center',
      maxWidth: signatureWidth - 5
    })

    // Line for signature
    doc.setLineWidth(0.1)
    doc.line(xPos + 5, lineY, xPos + signatureWidth - 5, lineY)

    // Value (printed name)
    doc.setFontSize(7)
    doc.text(signatureValues[i], xPos + signatureWidth / 2, valueY, {
      align: 'center',
      maxWidth: signatureWidth - 5
    })
    doc.setFontSize(8)
  }

  // Save PDF
  const filename = `Surat_Permintaan_${formatDate(data.tanggal).replace(/\//g, '_')}.pdf`
  doc.save(filename)
}

/**
 * Print PDF untuk Surat Permintaan (menggunakan browser print dialog)
 */
export const printSuratPermintaanPDF = async (data: SuratPermintaanData): Promise<void> => {
  const doc = new jsPDF('p', 'mm', 'a4')
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 15
  let yPos = margin

  // Set font
  doc.setFontSize(10)

  // Header Section - Load and add logo
  try {
    const logoBase64 = await imageToBase64(logoImage)
    // Add logo with appropriate size (logo height sekitar 20mm)
    const logoWidth = 30
    const logoHeight = 15
    doc.addImage(logoBase64, 'PNG', margin, yPos, logoWidth, logoHeight)
    yPos = yPos + logoHeight + 5 // Adjust yPos after logo
  } catch (error) {
    console.error('Error loading logo:', error)
    // Fallback to text if logo fails to load
    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    doc.text('PT Kian Santang Muliatama Tbk', margin, yPos + 10)
    yPos = yPos + 10
  }

  // Document info (top right) - pastikan tidak overlap dengan logo
  doc.setFontSize(8)
  const docInfoX = pageWidth - margin - 50
  const docInfoY = margin
  doc.text('No. Dok: FM-KSM-WH-08', docInfoX, docInfoY)
  doc.text('Revisi: 00', docInfoX, docInfoY + 5)
  doc.text('Tgl Efektif: 28/01/2019', docInfoX, docInfoY + 10)
  doc.text('Halaman: Page 1 of 1', docInfoX, docInfoY + 15)

  // Title - beri jarak lebih jauh dari header untuk menghindari overlap
  yPos = Math.max(yPos, 35) // Ensure minimum spacing
  doc.setFontSize(14)
  doc.setFont('helvetica', 'bold')
  doc.text('PERMOHONAN PENGAMBILAN BARANG', margin, yPos, {
    align: 'left'
  })

  // Tanggal
  yPos = yPos + 10
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('Tanggal:', margin, yPos)
  doc.text(formatDate(data.tanggal), margin + 25, yPos)

  // Table Section - beri jarak dari tanggal
  yPos = yPos + 8

  // Prepare table data
  const tableData = data.items.map((item) => {
    let sumberBarang = ''
    if (item.sumberBarang.proyek) {
      sumberBarang = `Proyek: ${item.sumberBarang.proyekValue || ''}`
    } else if (item.sumberBarang.stok) {
      sumberBarang = item.sumberBarang.stokValue ? `Stok: ${item.sumberBarang.stokValue}` : 'Stok'
    }

    const peruntukanParts: string[] = []
    if (item.peruntukan.proyek) {
      peruntukanParts.push(`Proyek: ${item.peruntukan.proyekValue || ''}`)
    }
    if (item.peruntukan.produksi) {
      peruntukanParts.push(`Produksi: ${item.peruntukan.produksiValue || ''}`)
    }
    if (item.peruntukan.kantor) {
      peruntukanParts.push('Kantor')
    }
    if (item.peruntukan.lainLain) {
      peruntukanParts.push('Lain-lain')
    }
    const peruntukan = peruntukanParts.join(', ')

    // Format qty to preserve decimal values (e.g., 1.2 instead of 1)
    // Use toFixed(2) to ensure 2 decimal places, then remove trailing zeros for cleaner display
    const qtyFormatted = item.qty 
      ? (() => {
          const num = typeof item.qty === 'number' ? item.qty : parseFloat(item.qty.toString())
          return num.toFixed(2).replace(/\.?0+$/, '')
        })()
      : ''
    
    return [
      item.no.toString(),
      item.kodeBarang || '',
      item.namaBarang || '',
      qtyFormatted,
      item.sat || '',
      sumberBarang,
      peruntukan || ''
    ]
  })

  autoTable(doc, {
    startY: yPos,
    head: [
      [
        'NO.',
        'KODE BARANG',
        'NAMA BARANG',
        'QTY',
        'SAT.',
        'SUMBER BARANG (Acc.)',
        'PERUNTUKAN'
      ]
    ],
    body: tableData,
    theme: 'grid',
    headStyles: {
      fillColor: [255, 255, 255],
      textColor: [0, 0, 0],
      fontStyle: 'bold',
      fontSize: 8,
      halign: 'center'
    },
    bodyStyles: {
      fontSize: 8,
      cellPadding: 2
    },
    columnStyles: {
      0: { cellWidth: 10, halign: 'center' },
      1: { cellWidth: 25, halign: 'left' },
      2: { cellWidth: 35, halign: 'left' },
      3: { cellWidth: 15, halign: 'center' },
      4: { cellWidth: 15, halign: 'center' },
      5: { cellWidth: 35, halign: 'left' },
      6: { cellWidth: 40, halign: 'left' }
    },
    styles: {
      lineWidth: 0.1,
      lineColor: [0, 0, 0]
    },
    margin: { left: margin, right: margin }
  })

  const finalY = (doc as any).lastAutoTable.finalY || yPos + 100

  // Footer Section (Signatures)
  yPos = finalY + 15

  const signatureWidth = (pageWidth - 2 * margin) / 5
  const signatureLabels = [
    'Pemohon\n(Mandor)',
    'Menyetujui\n(PIC)',
    'Yang Menyerahkan',
    'Mengetahui\n(SPV)',
    'Mengetahui\nAdmin Gudang'
  ]

  const signatureValues = [
    data.signatures.pemohon || '',
    data.signatures.menyetujui || '',
    data.signatures.yangMenyerahkan || '',
    data.signatures.mengetahuiSPV || '',
    data.signatures.mengetahuiAdminGudang || ''
  ]

  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')

  for (let i = 0; i < 5; i++) {
    const xPos = margin + i * signatureWidth
    const labelY = yPos
    const valueY = yPos + 25
    const lineY = yPos + 20

    doc.text(signatureLabels[i], xPos + signatureWidth / 2, labelY, {
      align: 'center',
      maxWidth: signatureWidth - 5
    })

    doc.setLineWidth(0.1)
    doc.line(xPos + 5, lineY, xPos + signatureWidth - 5, lineY)

    doc.setFontSize(7)
    doc.text(signatureValues[i], xPos + signatureWidth / 2, valueY, {
      align: 'center',
      maxWidth: signatureWidth - 5
    })
    doc.setFontSize(8)
  }

  // Open print dialog
  const pdfBlob = doc.output('blob')
  const url = URL.createObjectURL(pdfBlob)
  const printWindow = window.open(url, '_blank')
  
  if (printWindow) {
    printWindow.onload = () => {
      printWindow.print()
      URL.revokeObjectURL(url)
    }
  }
}

/**
 * Generate PDF untuk Surat Jalan (Delivery Slip)
 */
export const generateSuratJalanPDF = async (data: SuratJalanData): Promise<void> => {
  const doc = new jsPDF('p', 'mm', 'a4')
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 15
  let yPos = margin

  // Set font
  doc.setFontSize(10)

  // Header Section - Load and add logo
  try {
    const logoBase64 = await imageToBase64(logoImage)
    const logoWidth = 30
    const logoHeight = 15
    doc.addImage(logoBase64, 'PNG', margin, yPos, logoWidth, logoHeight)
    // Title - DELIVERY SLIP (right side) - naik 3x dari posisi saat ini (sekitar 12mm ke atas)
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    const titleX = pageWidth - margin - 50
    doc.text('DELIVERY SLIP', titleX, yPos + 3, { align: 'right' })
    yPos = yPos + logoHeight + 5
  } catch (error) {
    console.error('Error loading logo:', error)
    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    doc.text('PT Kian Santang Muliatama Tbk', margin, yPos + 10)
    // Title - DELIVERY SLIP (right side) - naik 3x dari posisi saat ini (sekitar 12mm ke atas)
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    const titleX = pageWidth - margin - 50
    doc.text('DELIVERY SLIP', titleX, yPos + 3, { align: 'right' })
    yPos = yPos + 10
  }

  // Horizontal line after header
  yPos = Math.max(yPos, 35)
  doc.setLineWidth(0.5)
  doc.line(margin, yPos, pageWidth - margin, yPos)
  yPos = yPos + 8

  // Top Information Section
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  
  // NO. FORM
  doc.text('NO. FORM:', margin, yPos)
  doc.setFont('helvetica', 'bold')
  doc.text(data.nomorForm, margin + 25, yPos)
  
  // KEPADA
  yPos = yPos + 7
  doc.setFont('helvetica', 'normal')
  doc.text('KEPADA:', margin, yPos)
  doc.setFont('helvetica', 'bold')
  doc.text(data.kepada, margin + 25, yPos)
  
  // Tanggal Pengiriman (right side)
  doc.setFont('helvetica', 'normal')
  doc.text('Tanggal Pengiriman :', pageWidth - margin - 60, yPos - 7, { align: 'right' })
  doc.setFont('helvetica', 'bold')
  doc.text(formatDate(data.tanggalPengiriman), pageWidth - margin, yPos - 7, { align: 'right' })

  // Table Section
  yPos = yPos + 10

  // Prepare table data - dinamis mengikuti jumlah item yang ada
  const tableData = data.items.map((item) => {
    const qtyFormatted = typeof item.qty === 'number' ? item.qty.toString() : item.qty
    return [
      item.no.toString(),
      item.namaBarang || '',
      qtyFormatted,
      item.ket || ''
    ]
  })

  autoTable(doc, {
    startY: yPos,
    head: [['NO', 'NAMA BARANG', 'QTY', 'KET']],
    body: tableData,
    theme: 'grid',
    headStyles: {
      fillColor: [255, 255, 255],
      textColor: [0, 0, 0],
      fontStyle: 'bold',
      fontSize: 10,
    },
    bodyStyles: {
      fontSize: 9,
    },
    columnStyles: {
      0: { cellWidth: 15, halign: 'center' },
      1: { cellWidth: 100 },
      2: { cellWidth: 25, halign: 'center' },
      3: { cellWidth: 45 },
    },
    margin: { left: margin, right: margin },
    styles: {
      lineColor: [0, 0, 0],
      lineWidth: 0.1,
    },
  })

  // Get final Y position after table
  const finalY = (doc as any).lastAutoTable.finalY || yPos + 100

  // Footer Section
  yPos = finalY + 10

  // Left side - Pemberi
  const footerLeftX = margin
  const footerRightX = pageWidth / 2 + 10
  const signatureLineY = yPos + 20

  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('Nama Pemberi:', footerLeftX, yPos)
  if (data.namaPemberi) {
    doc.setFont('helvetica', 'bold')
    doc.text(data.namaPemberi, footerLeftX + 30, yPos)
  }

  yPos = yPos + 7 + 28 // Turun 4x (7 * 4 = 28mm)
  doc.setFont('helvetica', 'normal')
  doc.text('TTD:', footerLeftX, yPos)
  
  // Signature line
  doc.setLineWidth(0.1)
  doc.line(footerLeftX + 15, yPos - 2, footerLeftX + 80, yPos - 2)

  yPos = yPos + 5 - 28 // Naik 4x (7 * 4 = 28mm) dari posisi saat ini
  doc.setFontSize(8)
  doc.setFont('helvetica', 'italic')
  doc.text('Note : Please sign and return to sender', footerLeftX, yPos)

  // Right side - Penerima
  yPos = finalY + 10
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('Tanggal Diterima :', footerRightX, yPos)
  if (data.tanggalDiterima) {
    doc.setFont('helvetica', 'bold')
    doc.text(formatDate(data.tanggalDiterima), footerRightX + 50, yPos)
  }

  yPos = yPos + 7
  doc.setFont('helvetica', 'normal')
  doc.text('Nama Penerima', footerRightX, yPos)
  if (data.namaPenerima) {
    doc.setFont('helvetica', 'bold')
    doc.text(data.namaPenerima, footerRightX + 40, yPos)
  }

  yPos = yPos + 7 + 28 // Turun 4x (7 * 4 = 28mm)
  doc.setFont('helvetica', 'normal')
  doc.text('TTD:', footerRightX, yPos)
  
  // Signature line
  doc.setLineWidth(0.1)
  doc.line(footerRightX + 15, yPos - 2, footerRightX + 80, yPos - 2)

  // Save PDF
  const filename = `Surat_Jalan_${data.nomorForm.replace(/\//g, '_')}.pdf`
  doc.save(filename)
}

/**
 * Print PDF untuk Surat Jalan (menggunakan browser print dialog)
 */
export const printSuratJalanPDF = async (data: SuratJalanData): Promise<void> => {
  const doc = new jsPDF('p', 'mm', 'a4')
  const pageWidth = doc.internal.pageSize.getWidth()
  const pageHeight = doc.internal.pageSize.getHeight()
  const margin = 15
  let yPos = margin

  // Set font
  doc.setFontSize(10)

  // Header Section - Load and add logo
  try {
    const logoBase64 = await imageToBase64(logoImage)
    const logoWidth = 30
    const logoHeight = 15
    doc.addImage(logoBase64, 'PNG', margin, yPos, logoWidth, logoHeight)
    // Title - DELIVERY SLIP (right side) - naik 3x dari posisi saat ini (sekitar 12mm ke atas)
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    const titleX = pageWidth - margin - 50
    doc.text('DELIVERY SLIP', titleX, yPos + 3, { align: 'right' })
    yPos = yPos + logoHeight + 5
  } catch (error) {
    console.error('Error loading logo:', error)
    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    doc.text('PT Kian Santang Muliatama Tbk', margin, yPos + 10)
    // Title - DELIVERY SLIP (right side) - naik 3x dari posisi saat ini (sekitar 12mm ke atas)
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    const titleX = pageWidth - margin - 50
    doc.text('DELIVERY SLIP', titleX, yPos + 3, { align: 'right' })
    yPos = yPos + 10
  }

  // Horizontal line after header
  yPos = Math.max(yPos, 35)
  doc.setLineWidth(0.5)
  doc.line(margin, yPos, pageWidth - margin, yPos)
  yPos = yPos + 8

  // Top Information Section
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  
  // NO. FORM
  doc.text('NO. FORM:', margin, yPos)
  doc.setFont('helvetica', 'bold')
  doc.text(data.nomorForm, margin + 25, yPos)
  
  // KEPADA
  yPos = yPos + 7
  doc.setFont('helvetica', 'normal')
  doc.text('KEPADA:', margin, yPos)
  doc.setFont('helvetica', 'bold')
  doc.text(data.kepada, margin + 25, yPos)
  
  // Tanggal Pengiriman (right side)
  doc.setFont('helvetica', 'normal')
  doc.text('Tanggal Pengiriman :', pageWidth - margin - 60, yPos - 7, { align: 'right' })
  doc.setFont('helvetica', 'bold')
  doc.text(formatDate(data.tanggalPengiriman), pageWidth - margin, yPos - 7, { align: 'right' })

  // Table Section
  yPos = yPos + 10

  // Prepare table data - dinamis mengikuti jumlah item yang ada
  const tableData = data.items.map((item) => {
    const qtyFormatted = typeof item.qty === 'number' ? item.qty.toString() : item.qty
    return [
      item.no.toString(),
      item.namaBarang || '',
      qtyFormatted,
      item.ket || ''
    ]
  })

  autoTable(doc, {
    startY: yPos,
    head: [['NO', 'NAMA BARANG', 'QTY', 'KET']],
    body: tableData,
    theme: 'grid',
    headStyles: {
      fillColor: [255, 255, 255],
      textColor: [0, 0, 0],
      fontStyle: 'bold',
      fontSize: 10,
    },
    bodyStyles: {
      fontSize: 9,
    },
    columnStyles: {
      0: { cellWidth: 15, halign: 'center' },
      1: { cellWidth: 100 },
      2: { cellWidth: 25, halign: 'center' },
      3: { cellWidth: 45 },
    },
    margin: { left: margin, right: margin },
    styles: {
      lineColor: [0, 0, 0],
      lineWidth: 0.1,
    },
  })

  // Get final Y position after table
  const finalY = (doc as any).lastAutoTable.finalY || yPos + 100

  // Footer Section
  yPos = finalY + 10

  // Left side - Pemberi
  const footerLeftX = margin
  const footerRightX = pageWidth / 2 + 10

  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('Nama Pemberi:', footerLeftX, yPos)
  if (data.namaPemberi) {
    doc.setFont('helvetica', 'bold')
    doc.text(data.namaPemberi, footerLeftX + 30, yPos)
  }

  yPos = yPos + 7 + 28 // Turun 4x (7 * 4 = 28mm)
  doc.setFont('helvetica', 'normal')
  doc.text('TTD:', footerLeftX, yPos)
  
  // Signature line
  doc.setLineWidth(0.1)
  doc.line(footerLeftX + 15, yPos - 2, footerLeftX + 80, yPos - 2)

  yPos = yPos + 5 // Naik 4x (7 * 4 = 28mm) dari posisi saat ini
  doc.setFontSize(8)
  doc.setFont('helvetica', 'italic')
  doc.text('Note : Please sign and return to sender', footerLeftX, yPos)

  // Right side - Penerima
  yPos = finalY + 10
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('Tanggal Diterima :', footerRightX, yPos)
  if (data.tanggalDiterima) {
    doc.setFont('helvetica', 'bold')
    doc.text(formatDate(data.tanggalDiterima), footerRightX + 50, yPos)
  }

  yPos = yPos + 7
  doc.setFont('helvetica', 'normal')
  doc.text('Nama Penerima', footerRightX, yPos)
  if (data.namaPenerima) {
    doc.setFont('helvetica', 'bold')
    doc.text(data.namaPenerima, footerRightX + 40, yPos)
  }

  yPos = yPos + 7 + 28 // Turun 4x (7 * 4 = 28mm)
  doc.setFont('helvetica', 'normal')
  doc.text('TTD:', footerRightX, yPos)
  
  // Signature line
  doc.setLineWidth(0.1)
  doc.line(footerRightX + 15, yPos - 2, footerRightX + 80, yPos - 2)

  // Open print dialog
  const pdfBlob = doc.output('blob')
  const url = URL.createObjectURL(pdfBlob)
  const printWindow = window.open(url, '_blank')
  
  if (printWindow) {
    printWindow.onload = () => {
      printWindow.print()
      URL.revokeObjectURL(url)
    }
  }
}

