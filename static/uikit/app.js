// Invoke Functions Call on Document Loaded
document.addEventListener('DOMContentLoaded', function () {
  hljs.highlightAll();

  const closeMessage = document.querySelector('.message-close');
  if (closeMessage) {
    closeMessage.addEventListener('click', () => {
      const messageWrapper = document.querySelector('.message');
      messageWrapper.style.display = 'none';
    });
  }
});
