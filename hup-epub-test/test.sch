<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron">
<ns uri="http://www.w3.org/1999/xhtml" prefix="html"/>
<ns uri="http://www.idpf.org/2007/ops" prefix="epub"/>
    <pattern id="primary">
        <rule context="html:body">
            <assert test="@epub:type = 'bodymatter'">body should be @epub:type 'bodymatter'</assert>
            <assert test="html:article">there is not an article</assert>
        </rule>
        <rule context="html:article">
            <assert test="@role='main'"><name/> at <value-of select='position()'/> needs aria @role 'main'</assert>
            <assert test="@epub:type='chapter'">article needs @epub:type 'chapter'</assert>
        </rule>
        <rule context="html:img">
            <assert test="@alt">Alt tag missing from img</assert>
            <report test="@alt='image'">No alt text supplied (found 'image')</report>
            <report test="@alt=''">@alt found, but empty</report>
        </rule>
        <rule context="html:table">
            <assert test="*//html:tr[@role='row']">table rows need aria role 'row'</assert>
            <assert test="preceding-sibling::html:img">no fallback image</assert>
            <assert test="preceding-sibling::html:img[@class='fallback']">fallback image missing class</assert>
        </rule>
        <rule context="html:blockquote">
            <assert test="@class"><name/> at <value-of select='position()'/> has no @class.</assert>
            <assert test="@class='epigraph' or @class='extract'">class mismatch for blockquote</assert>
        </rule>
        <rule context="html:aside">
            <assert test="@class='sidebar'">aside is normally a sidebar</assert>
            <assert test="@role='complementary'">aside needs an aria role</assert>
        </rule>
        <rule context="html:section/html:h1">
            <assert test="starts-with(@class, 'head')">H1 has no 'head' class</assert>
            <assert test="contains(@class, '-head') or contains(@class, '-subhead')">H1 has no head-type class</assert>
        </rule>
    </pattern>
</schema>
