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
            <assert test="@role='main'">article needs aria @role 'main'</assert>
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
        </rule>
        <rule context="html:blockquote">
            <assert test="@class">no style applied to blockquote</assert>
            <assert test="@class='epigraph' or @class='extract'">class mismatch for blockquote</assert>
        </rule>
    </pattern>
</schema>
