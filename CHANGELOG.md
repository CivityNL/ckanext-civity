# Changelog
The file contains all specific changes to the ckanext-civity.
## v2.6.x
* `civity`
  * WCAG-2.2 AA Compliance
    * Adjust multiple css properties to resolve 'color-contrast' violation - [CIVDEV-1560](https://civity.atlassian.net/browse/CIVDEV-1560)

## v2.7.0 (2025-07-21)
  - Added Config Option to enable/disable Accessibility Page and Footer ([CIVDEV-1604](https://civity.atlassian.net/browse/CIVDEV-1604))

## v2.6.0 (2025-06-30)
- `civity` 
  - Updated company address values in footer  ([CIVDEV-1076](https://civity.atlassian.net/browse/CIVDEV-1076))
  - Added Accessibility Page and Footer link to it ([CIVDEV-1589](https://civity.atlassian.net/browse/CIVDEV-1589))

## v2.5.0 (2025-05-05)
- `civity` 
  - Update schema to comply with ckanext-scheming `3.0.0+civity.3` -- ([CIVDEV-1350](https://civity.atlassian.net/browse/CIVDEV-1350)) 
    - Replace `group` with `field_group` in the schema fields attributes.

## 2.4.1 (2025-01-13)
- `civity`
  - Improved CivityHarvester -- ([CIVDEV-1067](https://civity.atlassian.net/browse/CIVDEV-1067))
    - Fixed issues when imported package changes name
    - Added support for easier extendability when creating Resource, DataStore and Default Resource Views.
  - Fixed bug in IPackageController after_search implementation of the IFacetLabelFunction not being called on each item -- ([CIVDEV-1195](https://civity.atlassian.net/browse/CIVDEV-1195))
  - Update `ckanext/civity/scheming/organization_multi_schemas/ckan-dataplatform-nl.json` to a list, to avoid issues with `load_multi_schema` function.

## 2.3.0 (2024-10-28)
- `civity`
  - Added a CLI command to assign all datasets to the correct theme groups -- ([CIVDEV-1056](https://civity.atlassian.net/browse/CIVDEV-1056))

## 2.2.0 (TBD)
- `civity`
  - Updated `webassets.yml` to fix issues with JavaScript modules -- ([CIVDEV-1093](https://civity.atlassian.net/browse/CIVDEV-1093))

## 2.1.0 (2024-09-16)
- `civity` 
  - Removed unused helper for create_on_ui_requires_resources -- ([CIVDEV-1032](https://civity.atlassian.net/browse/CIVDEV-1032))


## 2.0.0 (2024-08-30)

- First Version documented
