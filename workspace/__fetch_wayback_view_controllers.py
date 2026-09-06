import requests

cands=[
    'http://bilbo.cs.illinois.edu:80/page/publication_view/view-controller.js',
    'http://bilbo.cs.illinois.edu:80/page/publications/view-controller.js',
    'http://bilbo.cs.illinois.edu:80/page/resource_view/view-controller.js',
    'http://bilbo.cs.illinois.edu:80/page/software_view/view-controller.js',
    'http://bilbo.cs.illinois.edu:80/page/demo_view/view-controller.js',
    'http://bilbo.cs.illinois.edu:80/page/data/view-controller.js',
    'http://bilbo.cs.illinois.edu:80/page/data/index-controller.js',
    'http://bilbo.cs.illinois.edu:80/page/publications/controller.js',
    'http://bilbo.cs.illinois.edu:80/chunks/page-footer.html',
    'http://bilbo.cs.illinois.edu:80/chunks/page-header.html',
]

for u in cands:
    wb='https://web.archive.org/web/20190420080619id_/'+u
    try:
        r=requests.get(wb,timeout=60,headers={'User-Agent':'Mozilla/5.0'})
        print(r.status_code,len(r.text),u)
        if r.status_code==200:
            out='__wb_'+u.replace('http://','').replace(':80/','_').replace('/','_')
            if '.' not in out.split('_')[-1]:
                out += '.txt'
            with open(out,'w',encoding='utf-8',errors='ignore') as f:
                f.write(r.text)
    except Exception as ex:
        print('ERR',u,ex)
