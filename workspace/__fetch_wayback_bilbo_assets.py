import requests

items=[
('20160624195924','http://bilbo.cs.illinois.edu/index-controller.js','__wb_index_controller_20160624.js'),
('20160624121717','http://bilbo.cs.illinois.edu/nav/nav-controller.js','__wb_nav_controller_20160624.js'),
('20160624154950','http://bilbo.cs.illinois.edu/~kchang10/index.html','__wb_kchang_index_20160624.html'),
('20180906060746','http://bilbo.cs.illinois.edu:80/index.html','__wb_root_index_20180906.html'),
('20180906060831','http://bilbo.cs.illinois.edu:80/page/publications/','__wb_publications_20180906.html'),
('20180906060836','http://bilbo.cs.illinois.edu:80/page/resource_view/%7B%7Bdata.data[0].id%7D%7D','__wb_resource_view_20180906.html'),
]
for ts,orig,out in items:
    wb=f'https://web.archive.org/web/{ts}id_/{orig}'
    r=requests.get(wb,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
    print(out,r.status_code,len(r.text),wb)
    if r.status_code==200:
        open(out,'w',encoding='utf-8',errors='ignore').write(r.text)
