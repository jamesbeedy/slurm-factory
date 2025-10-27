import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  // Manually curated sidebar for Slurm Factory documentation
  tutorialSidebar: [
    'index', // Homepage/Overview
    'overview', // Project Overview
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'installation',
        'examples',
      ],
    },
    {
      type: 'category',
      label: 'Guides',
      items: [
        'deployment',
        'optimization',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'architecture',
        'api-reference',
      ],
    },
    {
      type: 'category',
      label: 'Support',
      items: [
        'troubleshooting',
        'contact',
        'contributing',
      ],
    },
  ],
};

export default sidebars;

