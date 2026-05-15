(function() {
    const data = {};

    // Название
    const titleEl = document.querySelector('h1');
    data.title = titleEl?.innerText?.trim() || '';

    // Ингредиенты
    const ingredients = [];
    document.querySelectorAll('.ingredient .name').forEach(el => {
        ingredients.push(el.innerText.trim().toLowerCase());
    });
    data.ingredients = ingredients;

    // Инструкция
    let instructions = '';
    document.querySelectorAll('.method-preparation .instruction, .ptab.vtab.method-preparation .instruction').forEach((step, idx) => {
        let text = step.innerText?.trim() || '';
        if (text && !text.includes('adfox') && !text.includes('adsbygoogle') && text.length > 20) {
            instructions += `${idx+1}. ${text}\n`;
        }
    });
    data.instructions = instructions;

    // Видео из data-src
    let videoUrl = '';
    const galleryEl = document.querySelector('.foto_gallery[data-src*="rutube"]');
    if (galleryEl) {
        videoUrl = galleryEl.getAttribute('data-src');
    }
    data.video = videoUrl || '';

    // Ссылка на оригинал
    data.link = window.location.href;

    // Время
    let timeMatch = document.querySelector('.method-preparation')?.innerText?.match(/(\d+)\s*мин/i);
    if (!timeMatch) {
        timeMatch = document.body.innerText.match(/(\d+)\s*мин/i);
    }
    data.time = timeMatch ? parseInt(timeMatch[1]) : null;

    console.log(JSON.stringify(data, null, 2));
})();