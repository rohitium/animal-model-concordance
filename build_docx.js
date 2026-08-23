const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,ShadingType,
       HeadingLevel,AlignmentType,ExternalHyperlink,BorderStyle,PageOrientation}=require('docx');
const rows=JSON.parse(fs.readFileSync('data/db/table_export.json','utf8'));

const W=[1700,1500,10240];              // DXA, sums to 13440 (landscape Letter minus margins)
const HEAD='2E3B4E', ZEBRA='F4F6F8';
const cell=(children,opts={})=>new TableCell({width:{size:opts.w,type:WidthType.DXA},
  shading:opts.fill?{type:ShadingType.CLEAR,fill:opts.fill,color:'auto'}:undefined,
  margins:{top:80,bottom:80,left:110,right:110},children});
const p=(runs,opts={})=>new Paragraph({spacing:{after:opts.after??40},children:runs});
const t=(text,o={})=>new TextRun({text,bold:o.b,italics:o.i,size:o.size??19,
  color:o.color,font:'Calibri'});

const header=new TableRow({tableHeader:true,children:
  ['Assessment','Model organism','Evidence'].map((h,i)=>
    cell([p([t(h,{b:true,size:19,color:'FFFFFF'})],{after:0})],{w:W[i],fill:HEAD}))});

const body=rows.map((r,idx)=>{
  const fill=idx%2?ZEBRA:undefined;
  const org=[p([t(r.organism,{b:true})],{after:20}),
             p([t(`${r.n_studies} ${r.n_studies===1?'study':'studies'}`,{size:17,color:'666666'})],{after:20}),
             ...r.verdicts.map(v=>p([t(`${v.n} ${v.label}`,{size:16,color:'666666'})],{after:0}))];
  const ev=[];
  // Lead with the synthesis. A list of extracted figures is not a finding: a reader
  // cannot tell from "3-70% proportion" which way the evidence points.
  if(r.direction) ev.push(p([t(r.direction.toUpperCase(),{b:true,size:16,
      color:r.direction.startsWith('evidence favours')?'15603A':
            r.direction.startsWith('evidence does not')?'8A2727':'7A5B00'})],{after:40}));
  if(r.summary) ev.push(p([t(r.summary,{size:18})],{after:60}));
  if(r.negative_controls) ev.push(p([t('Negative controls. ',{b:true,size:17,color:'8A6D00'}),
      t(r.negative_controls+' These are designed to score low and are excluded from the reading above.',
        {i:true,size:17,color:'8A6D00'})],{after:50}));
  if(r.why_range_is_wide) ev.push(p([t('What varies across the range. ',{b:true,size:17,color:'555555'}),
      t(r.why_range_is_wide,{size:17,color:'555555'})],{after:60}));
  if(r.evidence.length) ev.push(p([t('Figures behind this row',{b:true,size:16,color:'666666'})],{after:30}));
  r.evidence.forEach(e=>{
    const runs=[t(e.value,{b:true}),t('  '+e.statistic+e.n+' — '+e.what+' (',{size:18})];
    e.cites.forEach((c,i)=>{
      if(i) runs.push(t(' · ',{size:18}));
      runs.push(new ExternalHyperlink({link:c.url,children:[
        new TextRun({text:c.text,size:18,color:'1155CC',underline:{},font:'Calibri'})]}));
    });
    runs.push(t(')',{size:18}));
    ev.push(p(runs,{after:70}));
  });
  if(r.caveat) ev.push(p([t('Caveat. ',{b:true,size:17,color:'8A6D00'}),
                          t(r.caveat,{i:true,size:17,color:'8A6D00'})],{after:40}));
  if(!ev.length) ev.push(p([t('—',{size:18})]));
  return new TableRow({children:[
    cell([p([t(r.assessment,{b:true})],{after:0})],{w:W[0],fill}),
    cell(org,{w:W[1],fill}),
    cell(ev,{w:W[2],fill})]});
});

const doc=new Document({sections:[{
  properties:{page:{size:{width:12240,height:15840,orientation:PageOrientation.LANDSCAPE},
                    margin:{top:720,bottom:720,left:720,right:720}}},
  children:[
    new Paragraph({heading:HeadingLevel.HEADING_1,spacing:{after:80},
      children:[t('How well do animal models predict human clinical outcomes?',{b:true,size:30})]}),
    p([t('Evidence by assessment and model organism. Each figure is reported as the study '
        +'reported it, in its own units. Nothing is averaged across studies; a range spans only '
        +'figures measuring the same thing. Grouped labels such as “rodent” are kept as reported '
        +'and never expanded into member species. Each row opens with a synthesis of what the '
        +'evidence shows; the underlying figures follow. Study names link to PubMed.',{size:18,color:'444444'})],{after:80}),
    p([t('Source: ',{size:18,color:'444444'}),
       new ExternalHyperlink({link:'https://rohitium.github.io/animal-model-concordance/',
         children:[new TextRun({text:'rohitium.github.io/animal-model-concordance',size:18,
                                color:'1155CC',underline:{},font:'Calibri'})]}),
       t('  ·  Not peer reviewed. Screening and extraction were model-assisted and have not '
        +'been verified by a second reader. Verdict reliability: two independent raters agree on '
        +'73% of studies (Cohen\u2019s kappa 0.58).',{size:18,color:'444444'})],{after:200}),
    new Table({columnWidths:W,width:{size:13440,type:WidthType.DXA},rows:[header,...body],
      borders:{top:{style:BorderStyle.SINGLE,size:2,color:'C9CFD6'},
               bottom:{style:BorderStyle.SINGLE,size:2,color:'C9CFD6'},
               left:{style:BorderStyle.SINGLE,size:2,color:'C9CFD6'},
               right:{style:BorderStyle.SINGLE,size:2,color:'C9CFD6'},
               insideHorizontal:{style:BorderStyle.SINGLE,size:2,color:'C9CFD6'},
               insideVertical:{style:BorderStyle.SINGLE,size:2,color:'C9CFD6'}}})
  ]}]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('exports/animal-model-concordance-table.docx',b);
  console.log('wrote exports/animal-model-concordance-table.docx',b.length,'bytes');});
