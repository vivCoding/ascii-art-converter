$("a").each((i, a) => {
    $(a).hover(() => {
        $(a).children("u").css("border-bottom", "0.15em white solid")
    }, () => {
        $(a).children("u").css("border-bottom", "none")
    })
});

