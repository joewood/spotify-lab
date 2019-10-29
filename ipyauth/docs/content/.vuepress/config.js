module.exports = {
    title: 'ipyauth',
    description: 'OAuth2 authentication from inside Jupyter notebooks',
    base: '/ipyauth/',
    dest: '../public',
    head: [['link', { rel: 'icon', href: `/key.png` }]],
    // serviceWorker: true,
    themeConfig: {
        repo: 'https://gitlab.com/oscar6echo/ipyauth',
        editLinks: false,
        editLinkText: 'Edit this page on GitLab',
        lastUpdated: 'Last Updated',
        algolia: {
            apiKey: 'c95bfdd0b7c6d8386302d7170baf2bd3',
            indexName: 'ipyauth',
        },
        nav: [
            {
                text: 'Overview',
                link: '/overview/purpose',
            },
            {
                text: 'User Guide',
                link: '/guide/install',
            },
            {
                text: 'Development',
                link: '/dev/dev_install',
            },
        ],
        sidebarDepth: 5,
        sidebar: [
            {
                title: 'Overview',
                collapsable: false,
                children: ['/overview/purpose', '/overview/id_providers'],
            },
            {
                title: 'User Guide',
                collapsable: false,
                children: [
                    // '',
                    '/guide/install',
                    '/guide/general',
                    '/guide/auth0',
                    '/guide/google',
                    '/guide/sgconnect',
                ],
            },
            {
                title: 'Developer',
                collapsable: false,
                children: [
                    '/dev/dev_install',
                    '/dev/publish',
                    '/dev/new_provider',
                ],
            },
        ],
    },
    markdown: {
        lineNumbers: false,
    },
};
